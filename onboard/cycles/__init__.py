from datetime import timedelta
from queue import Queue
import time
import threading
from serial import Serial
import os

from .events import EventManager, RevolutionEvent, SessionStartEvent, SessionEndEvent
from .sensors import GpioReader, SerialReader
from .logger import FileLogger
from .reporter import reporter_thread
from .analysis import RevolutionCalculator
from .stream import websocket_server
from .sessions import SessionWatcher

def main():
    persist_path = os.path.expanduser('~/cycles')
    if not os.path.isdir(persist_path):
        os.makedirs(persist_path)

    log_queue = Queue()

    calc = RevolutionCalculator(wheel_radius_cm=13.0)

    events = EventManager()
    session = SessionWatcher(events)
    session.daemon = True
    session.start()

    events.on(RevolutionEvent, lambda e: session.on_revolution(e))
    events.on(RevolutionEvent, lambda e: log_queue.put(e))
    events.on(RevolutionEvent, lambda e: calc.record_revolutions(e.timestamp))

    events.on(SessionStartEvent, lambda e: log_queue.put(e))
    events.on(SessionEndEvent, lambda e: log_queue.put(e))

    #events.on(PauseEvent, lambda e: log_queue.put(e))

    #serial = Serial('/dev/ttyACM0', 9600)
    #serial = Serial('/dev/ttyUSB0', 9600)
    #serial = Serial('/dev/cu.usbmodem1411', 9600)

    #reader = SerialReader(serial, events)
    reader = GpioReader(22, events)
    reader.daemon = True
    reader.start()

    logger = FileLogger(log_queue, persist_path)
    logger.daemon = True
    logger.start()

    reporter = threading.Thread(target=reporter_thread, args=(calc, timedelta(seconds=1)))
    reporter.daemon=True
    reporter.start()

    ws = threading.Thread(target=websocket_server, args=(calc, '0.0.0.0', 8765))
    ws.daemon = True
    ws.start()

    try:
        while True:
            reader.join(1)
    except KeyboardInterrupt:
        print("Stopping")


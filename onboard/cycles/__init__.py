from datetime import timedelta
from queue import Queue
import time
import threading
from serial import Serial
import os

from .events import EventManager, RevolutionEvent
from .sensors import serial_reader, gpio_poller
from .logger import file_persister
from .reporter import reporter_thread
from .analysis import RevolutionCalculator
from .stream import websocket_server

def main():
    persist_file_path = os.path.expanduser('~/cycles.txt')
    persist_file = open(persist_file_path, 'a', buffering=1)

    log_queue = Queue()

    calc = RevolutionCalculator(wheel_radius_cm=13.0)

    events = EventManager()
    events.on(RevolutionEvent, lambda e: log_queue.put(e))
    events.on(RevolutionEvent, lambda e: calc.record_revolutions(e.timestamp))

    #serial = Serial('/dev/ttyACM0', 9600)
    #serial = Serial('/dev/ttyUSB0', 9600)
    #serial = Serial('/dev/cu.usbmodem1411', 9600)

    #reader = threading.Thread(target=serial_reader, args=(serial, events))
    reader = threading.Thread(target=gpio_poller, args=(22, events))
    reader.daemon = True
    reader.start()

    logger = threading.Thread(target=file_persister, args=(log_queue, persist_file))
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

    persist_file.close()


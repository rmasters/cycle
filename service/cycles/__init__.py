from datetime import datetime, timedelta
import signal
import sys
import threading
import serial


class EventBus:
    def __init__(self):
        self.hooks = {}

    def on_event(self, event, hook_fn):
        event_name = type(event).__name__
        if event_name not in self.hooks:
            self.hooks[event_name] = []
        self.hooks[event_name].append(hook_fn)

    def emit(self, event):
        event_name = type(event).__name__
        if event_name in self.hooks:
            for hook in self.hooks[event_name]:
                hook(event)


class RevolutionEvent:
    name = 'revolution'

    def __init__(self, timestamp):
        self.timestamp = timestamp


class RevolutionPrinterListener:
    """Event listener that prints when revolutions occur"""
    def __init__(self, out_file):
        self.out_file = out_file

    def on_revolution(self, event):
        self.out_file.write("Revolution @ %s" % event.timestamp.stftime('%H:%M:%S.%f'))


class SerialReaderThread(threading.Thread):
    """Reads revolution lines from the serial port and emits events"""
    def __init__(self, device, baud, event_bus):
        self.serial = serial.Serial(device, baud)
        self.stopper = threading.Event()
        self.events = event_bus

    def run(self):
        start_time = datetime.now()
        self.serial.open()
        while True:
            if self.stopped():
                break

            line = self.serial.readline().decode()
            self.process_line(line, start_time)

        self.serial.close()

    def process_line(self, line, start_time):
        # Incoming lines are number of milliseconds elapsed since Arduino
        # program started running. In our case, we can base this off the time
        # we opened the serial connection. In practice, this overflows after
        # around 50 days.
        microseconds = int(line.strip())
        revolution_time = start_time + timedelta(microseconds)

        self.events.emit(RevolutionEvent(revolution_time))

    def stop(self):
        self.stopper.set()

    def stopped(self):
        return self.stopper.is_set()


class Cycle:
    def __init__(self, serial_reader):
        self.serial_reader = serial_reader

    def start(self):
        self.serial_reader.start()

        # Register signal catchers
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def stop(self, *args):
        self.serial_reader.stop()

        self.serial_reader.join()


def main():
    revolution_printer = RevolutionPrinterListener(sys.stdout)

    event_bus = EventBus()
    event_bus.on_event(RevolutionEvent, revolution_printer.on_revolution)

    serial_reader = SerialReaderThread('/dev/ttyUSB0', 9600, event_revolution)
    cycle = Cycle(serial_reader)

    try:
        cycle.start()
    except KeyboardInterrupt:
        cycle.stop()


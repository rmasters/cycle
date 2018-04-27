from datetime import datetime, timedelta
import signal
import sys
import time
import threading
import serial


class EventBus:
    def __init__(self):
        self.hooks = {}

    def on_event(self, event, hook_fn):
        event_name = self.event_name(event)
        if event_name not in self.hooks:
            self.hooks[event_name] = []
        self.hooks[event_name].append(hook_fn)

    def emit(self, event):
        event_name = self.event_name(event)
        if event_name in self.hooks:
            for hook in self.hooks[event_name]:
                hook(event)

    def event_name(self, v):
        return v.__name__ if type(v) == type else type(v).__name__


class RevolutionEvent:
    name = 'revolution'

    def __init__(self, timestamp):
        self.timestamp = timestamp


class RevolutionPrinterListener:
    """Event listener that prints when revolutions occur"""
    def __init__(self, out_file):
        self.out_file = out_file

    def on_revolution(self, event):
        self.out_file.write("Revolution @ %s\n" % event.timestamp.strftime('%H:%M:%S.%f'))


class SerialReaderThread(threading.Thread):
    """Reads revolution lines from the serial port and emits events"""
    def __init__(self, device, baud, event_bus):
        self.serial = serial.Serial(device, baud)
        self.stopper = threading.Event()
        self.events = event_bus

        super(SerialReaderThread, self).__init__(name='serial-reader')

    def run(self):
        start_time = datetime.now()
        #self.serial.open()
        while True:
            if self.stopped():
                break

            line = self.serial.readline().decode()
            self.process_line(line, start_time)

        #self.serial.close()

    def process_line(self, line, start_time):
        # Incoming lines are number of milliseconds elapsed since Arduino
        # program started running. In our case, we can base this off the time
        # we opened the serial connection. In practice, this overflows after
        # around 50 days.
        milliseconds = int(line.strip())
        revolution_time = start_time + timedelta(milliseconds=milliseconds)

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

    # mac: /dev/ttyUSB0
    # rpi: /dev/ttyACM0
    serial_reader = SerialReaderThread('/dev/ttyACM0', 9600, event_bus)
    cycle = Cycle(serial_reader)

    try:
        cycle.start()
    except KeyboardInterrupt:
        print("Stopping...")
        cycle.stop()


main()


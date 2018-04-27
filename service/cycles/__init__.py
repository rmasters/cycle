import signal
import threading
import serial


class EventBus:
    def __init__(self):
        self.hooks = {}

    def on_event(self, event_name, hook_fn):
        if event_name not in self.hooks:
            self.hooks[event_name] = []
        self.hooks[event_name].append(hook_fn)


class SerialReaderThread(threading.Thread):
    def __init__(self, device, baud):
        self.serial = serial.Serial(device, baud)
        self.stopper = threading.Event()

    def run(self):
        self.serial.open()
        while True:
            if self.stopped():
                break

            line = self.serial.readline()

        self.serial.close()

    def read_line(self, line):
        pass

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
    serial_reader = SerialReaderThread('/dev/ttyUSB0', 9600)
    cycle = Cycle(serial_reader)

    try:
        cycle.start()
    except KeyboardInterrupt:
        cycle.stop()


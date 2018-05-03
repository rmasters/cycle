from datetime import datetime, timedelta
import threading
from gpiozero import InputDevice
from .events import RevolutionEvent


class BaseReader(threading.Thread):
    def __init__(self, events):
        super(BaseReader, self).__init__()

        self.events = events

    def run(self):
        for timestamp in self.timestamp_generator():
            event = RevolutionEvent(timestamp)
            events.emit(event)

    def timestamp_generator(self):
        """
        Yield datetime.datetimes from here when a revolution happens

        """
        raise NotImplementedError()


class SerialReader(BaseReader):
    def __init__(self, serial, events):
        super(SerialReader, self).__init__(events)

        self.serial = serial

   def timestamp_generator(self):
        start_time = datetime.utcnow()
        while True:
            line = serial.readline().decode()

            millis = int(line.strip())
            rev_timestamp = start_time + timedelta(milliseconds=millis)
            yield rev_timestamp


class GpioReader(BaseReader):
    """
    A polling thread that watches a GPIO pin for signals

    Connect one wire to 3v3 and another to an input pin. e.g. board pins 17
    and 17 (BCM 22 and 3v3).

    """

    def __init__(self, gpio_pin, events):
        super(GpioReader, self).__init__(events)

        self.pin = gpio_pin

    def timestamp_generator(self):
        with InputDevice(self.pin) as p:
            while True:
                if p.value and not prev_value:
                    yield datetime.utcnow()

                    # Prevent repeated-firing when pedal is slow or left over the
                    # reed switch
                    prev_value = p.value
                elif not p.value and prev_value:
                    prev_value = p.value


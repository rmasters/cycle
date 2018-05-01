from datetime import datetime, timedelta
from gpiozero import InputDevice
from .events import RevolutionEvent

def serial_reader(serial, events):
    start_time = datetime.utcnow()
    while True:
        line = serial.readline().decode()

        millis = int(line.strip())
        rev_timestamp = start_time + timedelta(milliseconds=millis)

        event = RevolutionEvent(rev_timestamp)
        events.emit(event)

def gpio_poller(gpio_pin, events):
    """
    A polling thread that watches a GPIO pin for signals

    Connect one wire to 3v3 and another to an input pin. e.g. board pins 17
    and 17 (BCM 22 and 3v3).

    """

    with InputDevice(gpio_pin) as p:
        prev_value = None
        while True:
            if p.value and not prev_value:
                event = RevolutionEvent(datetime.utcnow())
                events.emit(event)

                # Prevent repeated-firing when pedal is slow or left over the
                # reed switch
                prev_value = p.value
            elif not p.value and prev_value:
                prev_value = p.value


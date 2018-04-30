from datetime import datetime, timedelta
from .events import RevolutionEvent

def serial_reader(serial, events):
    start_time = datetime.utcnow()
    while True:
        line = serial.readline().decode()

        millis = int(line.strip())
        rev_timestamp = start_time + timedelta(milliseconds=millis)

        event = RevolutionEvent(rev_timestamp)
        events.emit(event)


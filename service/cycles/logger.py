import time
from .events import StopEvent, RevolutionEvent


def file_persister(queue, persist_file):
    while True:
        # TODO: timeout here so that the StopEvent works?
        event = queue.get()

        # Catch break-out tasks
        if isinstance(event, StopEvent):
            queue.task_done()
            break

        if isinstance(event, RevolutionEvent):
            # Write a millisecond-accurate, UTC timestamp to the file
            # Datetime -> timestamp with milliseconds https://stackoverflow.com/a/8159893
            dt = event.timestamp
            timestamp = int((time.mktime(dt.utctimetuple()) + dt.microsecond / 1000000.0)*1000)

            persist_file.write(str(timestamp) + "\n")

            queue.task_done()
            continue

        queue.task_done()


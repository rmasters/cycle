import os
import time
import threading
from .events import StopEvent, RevolutionEvent, SessionStartEvent, SessionEndEvent


class FileLogger(threading.Thread):
    def __init__(self, queue, persist_dir):
        super(FileLogger, self).__init__()

        self.queue = queue
        self.persist_dir = persist_dir

        self.persist_file = None

    def run(self):
        while True:
            event = self.queue.get()

            if isinstance(event, RevolutionEvent):
                self.on_revolution(event)

            if isinstance(event, SessionStartEvent):
                self.on_session_start(event)

            if isinstance(event, SessionEndEvent):
                self.on_session_stop(event)

            self.queue.task_done()

    def on_revolution(self, event):
        # Write a millisecond-accurate, UTC timestamp to the file
        # Datetime -> timestamp with milliseconds https://stackoverflow.com/a/8159893
        dt = event.timestamp
        timestamp = int((time.mktime(dt.utctimetuple()) + dt.microsecond / 1000000.0)*1000)

        if self.persist_file is None:
            self.open_persist_file(event.timestamp)

        self.persist_file.write(str(timestamp) + "\n")

    def on_session_start(self, event):
        self.open_persist_file(event.started_at)

    def open_persist_file(self, timestamp):
        filename = "cyclelog-%s.log" % timestamp.strftime("%Y%m%d%H%M%S")
        persist_file_path = os.path.join(self.persist_dir, filename)

        self.persist_file = open(persist_file_path, 'a')

    def on_session_stop(self, event):
        if self.persist_file:
            self.persist_file.close()
            self.persist_file = None


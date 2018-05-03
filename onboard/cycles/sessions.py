from datetime import datetime, timedelta
import time
import threading
from .events import SessionStartEvent, SessionEndEvent, PauseEvent

class SessionWatcher(threading.Thread):
    def __init__(self, events, pause_timeout=None, session_timeout=None):
        super(SessionWatcher, self).__init__()

        self.events = events

        self.last_revolution = None

        self.pause_timeout = timedelta(seconds=10) if pause_timeout is None else pause_timeout
        self.session_timeout = timedelta(minutes=15) if session_timeout is None else session_timeout

    def run(self):
        while True:
            self.on_tick()
            time.sleep(1)

    def on_tick(self):
        if self.last_revolution is None:
            return

        now = datetime.utcnow()
        delta = now - self.last_revolution

        """
        Watch for breaks in cadence - we're looking for
        -   pause interval (default: 10s) - taking a break
        -   stop interval (default: 15m) - stopping the session

        """

        if delta >= self.session_timeout:
            self.events.emit(SessionEndEvent(self.last_revolution))
            return

        if delta >= self.pause_timeout:
            self.events.emit(PauseEvent(self.last_revolution))
            return

    def on_revolution(self, event):
        # If it's been a while since the last crank, start a new session
        if self.last_revolution is not None:
            if event.timestamp - self.last_revolution > self.session_timeout:
                self.events.emit(SessionStartEvent(event.timestamp))

        self.last_revolution = event.timestamp


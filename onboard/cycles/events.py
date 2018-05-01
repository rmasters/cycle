def get_event_name(event):
    # Class passed
    if type(event) == type:
        return event.__name__

    # Instance passed
    return type(event).__name__


class EventManager:
    """Simple event manager"""
    def __init__(self):
        self.hooks = {}

    def on(self, event_cls, hook):
        event_name = get_event_name(event_cls)

        if event_name not in self.hooks:
            self.hooks[event_name] = []

        self.hooks[event_name].append(hook)

    def emit(self, event):
        event_name = get_event_name(event)

        if event_name not in self.hooks:
            return

        for hook in self.hooks[event_name]:
            hook(event)


class RevolutionEvent:
    def __init__(self, timestamp):
        self.timestamp = timestamp


class SessionStartEvent:
    pass


class SessionEndEvent:
    pass

class StopEvent:
    pass


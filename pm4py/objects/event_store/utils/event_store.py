from pm4py.objects.log.log import Event
from pm4py.objects.log.log import EventStream


class EventStore(object):
    """
    Basic class to support event stores (shall be inherited
    and extended by specific versions)
    """

    def __init__(self):
        """
        Initialize the event store
        """
        self.event_stream = []
        self.observers = []

    def add_observer(self, observer):
        """
        Adds an observer to the event store

        Parameters
        ------------
        observer
            Observer
        """
        self.observers.append(observer)

    def remove_observer(self, obj):
        """
        Removes an observer from the event store

        Parameters
        -------------
        obj
            Index or object to remove from observers
        """
        if type(obj) is int:
            del self.observers[obj]
        del self.observers[self.observers.index(obj)]

    def get_stream(self):
        """
        Gets an event stream from the event store

        Returns
        -------------
        stream
            Event stream
        """
        return EventStream(self.event_stream)

    def before_push(self, event):
        """
        Version-specific function that is executed before pushing
        the event in the store

        Parameters
        -------------
        event
            Event
        """
        # version-specific, to be implemented
        pass

    def after_push(self, event):
        """
        Version-specific function that is executed after pushing
        the event in the store

        Parameters
        --------------
        event
            Event
        """
        # version-specific, to be implemented
        pass

    def push(self, event):
        """
        Push an event into the event store

        Parameters
        ---------------
        event
            Event (if it is a dictionary, then it is automatically converted to event)
        """
        if not type(event) is Event:
            event = Event(event)

        self.before_push(event)
        self.event_stream.append(event)
        for observer in self.observers:
            observer.update(event)
        self.after_push(event)

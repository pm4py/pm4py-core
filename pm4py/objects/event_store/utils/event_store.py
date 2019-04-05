from threading import Semaphore

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
        self.store_semaphore = Semaphore(1)

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
        self.store_semaphore.acquire()
        stream = EventStream(self.event_stream)
        self.store_semaphore.release()
        return stream

    def shall_be_added(self, event):
        """
        Version-specific function that is executed to see if the
        event should be part of the stream

        Parameters
        -------------
        event
            Event
        """
        return True

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

    def do_push(self, event):
        """
        Version-specific function that is executed to push
        the event in the store

        Parameters
        -------------
        event
            Event
        """
        self.event_stream.append(event)

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
        self.store_semaphore.acquire()
        if not type(event) is Event:
            event = Event(event)

        if self.shall_be_added(event):
            self.before_push(event)
            self.do_push(event)
            for observer in self.observers:
                observer.acquire()
                observer.update(event, self)
                observer.release()
            self.after_push(event)
        self.store_semaphore.release()

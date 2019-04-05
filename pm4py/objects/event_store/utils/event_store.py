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
        self.__event_stream = []
        self.__observers = []

    def add_observer(self, observer):
        """
        Adds an observer to the event store

        Parameters
        ------------
        observer
            Observer
        """
        self.__observers.append(observer)

    def remove_observer(self, obj):
        """
        Removes an observer from the event store

        Parameters
        -------------
        obj
            Index or object to remove from observers
        """
        if type(obj) is int:
            del self.__observers[obj]
        del self.__observers[self.__observers.index(obj)]

    def get_stream(self):
        """
        Gets an event stream from the event store

        Returns
        -------------
        stream
            Event stream
        """
        return EventStream(self.__event_stream)

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
        self.before_push(event)
        self.after_push(event)
        for observer in self.__observers:
            observer.update(event)

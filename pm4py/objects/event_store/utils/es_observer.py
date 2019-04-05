class EventStoreObserver(object):
    """
    Basic class to support observers on the event store
    (shall be inherited and extended by specific implementations)
    """
    def __init__(self, event_store):
        """
        Initialize the observer on the event store

        Parameters
        ------------
        event_store
            Event store
        """
        self.__event_store = event_store
        self.__event_store.add_observer(self)

    def update(self, event):
        """
        Update function that is called when the event
        is updated

        Parameters
        -------------
        event
            Event
        """
        # to be overriden
        pass

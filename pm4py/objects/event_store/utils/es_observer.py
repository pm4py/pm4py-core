from threading import Semaphore


class EventStoreObserver(object):
    """
    Basic class to support observers on the event store
    (shall be inherited and extended by specific implementations)
    """

    def __init__(self):
        """
        Initialize the observer
        """
        self.observer_semaphore = Semaphore(1)

    def acquire(self):
        """
        (Technical method) acquire the observer semaphore
        """
        self.observer_semaphore.acquire()

    def release(self):
        """
        (Technical method) release the observer semaphore
        """
        self.observer_semaphore.release()

    def update(self, event, event_store):
        """
        Update function that is called when the event
        is updated

        Parameters
        -------------
        event
            Event
        event_store
            Event store
        """
        # to be overriden
        pass

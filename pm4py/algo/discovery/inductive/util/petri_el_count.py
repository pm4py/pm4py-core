class Counts(object):
    """
    Shared variables among executions
    """

    def __init__(self):
        """
        Constructor
        """
        self.noOfPlaces = 0
        self.noOfHiddenTransitions = 0
        self.noOfVisibleTransitions = 0
        self.dictSkips = {}
        self.dictLoops = {}

    def inc_places(self):
        """
        Increase the number of places
        """
        self.noOfPlaces = self.noOfPlaces + 1

    def inc_noOfHidden(self):
        """
        Increase the number of hidden transitions
        """
        self.noOfHiddenTransitions = self.noOfHiddenTransitions + 1

    def inc_noOfVisible(self):
        """
        Increase the number of visible transitions
        """
        self.noOfVisibleTransitions = self.noOfVisibleTransitions + 1
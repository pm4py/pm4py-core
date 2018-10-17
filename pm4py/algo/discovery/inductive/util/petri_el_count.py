class Counts(object):
    """
    Shared variables among executions
    """

    def __init__(self):
        """
        Constructor
        """
        self.num_places = 0
        self.num_hidden = 0
        self.num_visible_trans = 0
        self.dict_skips = {}
        self.dict_loops = {}

    def inc_places(self):
        """
        Increase the number of places
        """
        self.num_places = self.num_places + 1

    def inc_no_hidden(self):
        """
        Increase the number of hidden transitions
        """
        self.num_hidden = self.num_hidden + 1

    def inc_no_visible(self):
        """
        Increase the number of visible transitions
        """
        self.num_visible_trans = self.num_visible_trans + 1

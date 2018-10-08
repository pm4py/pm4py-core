class ProcessTree:
    def __init__(self):
        """
        Constructor
        """
        # reset variables
        self.operator = 0
        self.children = 0

        self.operator = ""
        self.children = []

    def __repr__(self):
        return "ProcessTree: "
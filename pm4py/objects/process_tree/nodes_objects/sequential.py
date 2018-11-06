from pm4py.objects.process_tree.nodes_objects.nodeobject import NodeObject
from pm4py.objects.process_tree.nodes_threads import sequential as sequential_thread


class Sequential(NodeObject):
    def __init__(self, node):
        """
        Initialize the node object

        Parameters
        ----------
        node
            Node of the process tree
        """
        self.initialize_thread()
        NodeObject.__init__(self, node)

    def initialize_thread(self):
        """
        Initialize thread for current node object
        """
        self.node_thread = sequential_thread.Sequential(self)

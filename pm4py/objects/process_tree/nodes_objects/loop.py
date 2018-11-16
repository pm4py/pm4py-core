from pm4py.objects.process_tree.nodes_objects.nodeobject import NodeObject
from pm4py.objects.process_tree.nodes_threads import loop as loop_thread


class Loop(NodeObject):
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
        self.node_thread = loop_thread.Loop(self)

from pm4py.objects.process_tree.nodes_threads import parallel as parallel_thread
from pm4py.objects.process_tree.nodes_objects.nodeobject import NodeObject


class Parallel(NodeObject):
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
        self.node_thread = parallel_thread.Parallel(self)

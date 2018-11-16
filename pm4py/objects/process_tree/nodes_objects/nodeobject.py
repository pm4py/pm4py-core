class NodeObject(object):
    def __init__(self, node):
        """
        Initialize the node object

        Parameters
        ----------
        node
            Node of the process tree
        """
        self.node = node

    def get_children(self):
        """
        Get the children of the current node

        Returns
        -----------
        children
            Children of the current node
        """
        return self.node.children

    def generate_events_trace(self, conc_trace_obj):
        """
        Generate events adding them to the concurrent trace object

        Parameters
        -----------
        conc_trace_obj
            Concurrent trace object

        Returns
        -----------
        node_thread
            Current node thread
        """
        self.initialize_thread()
        self.node_thread.set_concurrent_trace_obj(conc_trace_obj)
        self.node_thread.start()

        if self.node.rec_depth == 0:
            self.node_thread.join()

        return self.node_thread

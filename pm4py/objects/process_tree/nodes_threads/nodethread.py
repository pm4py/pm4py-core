from threading import Thread


class NodeThread(Thread):
    def __init__(self, node_object):
        """
        Initialize the node thread providing the node object

        Parameters
        -----------
        node_object
            Object related to the node of the process tree
        """
        self.node_object = node_object
        Thread.__init__(self)

    def set_concurrent_trace_obj(self, conc_trace_obj):
        """
        Sets the concurrent trace object in order to append events to it

        Parameters
        -----------
        conc_trace_obj
            Concurrent trace object
        """
        self.conc_trace_obj = conc_trace_obj

    def run(self):
        """
        Runs the current thread (in order to generate the trace)
        """
        return None

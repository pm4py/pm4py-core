from pm4py.objects.process_tree.nodes_threads.nodethread import NodeThread
from pm4py.objects.process_tree import process_tree
from numpy.random import exponential

class Loop(NodeThread):
    def __init__(self, node_object):
        """
        Initialize the node thread providing the node object

        Parameters
        -----------
        node_object
            Object related to the node of the process tree
        """
        NodeThread.__init__(self, node_object)

    def run(self):
        """
        Runs the current thread (in order to generate the trace)
        """
        ch = self.node_object.get_children()

        if 2 <= len(ch) <= 3 and type(ch[0]) is process_tree.ProcessTree and type(ch[1]) is process_tree.ProcessTree:
            no_of_rep = int(exponential(scale=0.75)) + 1

            for i in range(no_of_rep):
                if i > 0:
                    # REDO
                    thr = ch[1].node_object.generate_events_trace(self.conc_trace_obj)
                    thr.join()

                # DO
                thr = ch[0].node_object.generate_events_trace(self.conc_trace_obj)
                thr.join()

            # EXIT
            thr = ch[-1].node_object.generate_events_trace(self.conc_trace_obj)
            thr.join()
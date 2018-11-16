from pm4py.objects.process_tree.nodes_threads.nodethread import NodeThread
from pm4py.objects.process_tree import process_tree
from random import shuffle


class Parallel(NodeThread):
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
        children = self.node_object.get_children()
        shuffle(children)
        threads = []
        for node in children:
            if type(node) is process_tree.PTTransition:
                if node.label is not None:
                    self.conc_trace_obj.add_visible_transition(node)
            elif type(node) is process_tree.ProcessTree:
                threads.append( node.node_object.generate_events_trace(self.conc_trace_obj))
        for thread in threads:
            thread.join()
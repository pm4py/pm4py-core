from pm4py.objects.process_tree.nodes_threads.nodethread import NodeThread


class Parallel(NodeThread):
    def __init__(self, node_object):
        NodeThread.__init__(self, node_object)

    def run(self):
        return None

from pm4py.objects.process_tree.nodes_objects.nodeobject import NodeObject


class Exclusive(NodeObject):
    def __init__(self, node_object):
        NodeObject.__init__(self, node_object)

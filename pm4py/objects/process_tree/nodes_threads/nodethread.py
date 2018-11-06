from threading import Thread


class NodeThread(Thread):
    def __init__(self, node_object):
        self.node_object = node_object
        Thread.__init__(self)

    def run(self):
        return None

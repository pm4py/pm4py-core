from pm4py.objects.petri_net.obj import Marking


class DataMarking(Marking):
    def __init__(self, marking=None):
        Marking.__init__(self, marking)
        self.data_dict = {}

    def __repr__(self):
        # return str([str(p.name) + ":" + str(self.get(p)) for p in self.keys()])
        # The previous representation had a bug, it took into account the order of the places with tokens
        return str([str(p.name) + ":" + str(self.get(p)) for p in sorted(list(self.keys()), key=lambda x: x.name)]) + " " + str(self.data_dict)

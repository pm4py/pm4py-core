from pm4py.algo.discovery.inductive.data_structures import process_tree

class ProcessTree(object):
    def __init__(self):
        """
        Constructor
        """
        # reset variables
        self.operator = 0
        self.rec_depth = 0

        self.operator = ""
        self.children = []

    def __repr__(self):
        if self.rec_depth == 0:
            ret_list = ["ProcessTree: "]
        else:
            ret_list = [""]

        ret_list.append(self.operator + "(")

        for index, child in enumerate(self.children):
            if index > 0:
                ret_list.append(",")
            ret_list.append(repr(child))

        ret_list.append(")")

        return "".join(ret_list)

    def add_subtree(self, subtree):
        self.children.append(subtree)

    def add_transition(self, trans):
        proceed_to_add = True
        if trans.label is None:
            if "skip" in trans.name:
                #print([type(x) for x in self.children])
                added_skip_trans = [x for x in self.children if type(x) is process_tree.PT_Transition and "skip" in x.name]
                if added_skip_trans:
                    proceed_to_add = False
        if proceed_to_add:
            self.children.append(trans)

class PT_Transition(object):
    def __init__(self, name, label):
        self.name = name
        self.label = label

    def __repr__(self):
        if self.label is not None:
            return self.label
        return self.name
from pm4py.algo.discovery.inductive.data_structures import process_tree, tree_constants

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
        """
        Obtains a string representation of the process tree

        Returns
        ---------
        string
            String representing the process tree
        """
        if self.rec_depth == 0:
            ret_list = ["ProcessTree: "]
        else:
            ret_list = [""]

        condition_wo_operator = self.operator == tree_constants.EXCLUSIVE_OPERATOR and len(self.children) == 1 and type(self.children[0]) is process_tree.PT_Transition

        if not condition_wo_operator:
            ret_list.append(self.operator + "(")

        for index, child in enumerate(self.children):
            if index > 0:
                ret_list.append(",")
            ret_list.append(repr(child))

        if not condition_wo_operator:
            ret_list.append(")")

        return "".join(ret_list)

    def add_subtree(self, subtree):
        """
        Adds a new subtree to the current one

        Parameters
        ----------
        subtree
            Subtree to add
        """
        self.children.append(subtree)

    def add_transition(self, trans):
        """
        Adds a new transition to the subtree

        Parameters
        ----------
        trans
            Transition to add (visible or invisible)
        """
        proceed_to_add = True
        if trans.label is None:
            if "skip" in trans.name:
                added_skip_trans = [x for x in self.children if
                                    type(x) is process_tree.PT_Transition and "skip" in x.name]
                if added_skip_trans:
                    proceed_to_add = False
        if proceed_to_add:
            self.children.append(trans)


class PT_Transition(object):
    def __init__(self, name, label):
        """
        Constructor

        Parameters
        ----------
        name
            Name of the transition on the Process Tree
        label
            Label of the transition on the Process Tree
        """
        self.name = name
        self.label = label

    def __repr__(self):
        """
        Gets a label for the transition
        """
        if self.label is not None:
            return self.label
        if len(self.name) > 0:
            return self.name.split("_")[0]
        return ""

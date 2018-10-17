from pm4py.objects.process_tree import tree_constants


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

        condition_wo_operator = self.operator == tree_constants.EXCLUSIVE_OPERATOR and len(self.children) == 1 and type(
            self.children[0]) is PTTransition

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
                                    type(x) is PTTransition and "skip" in x.name]
                if added_skip_trans:
                    proceed_to_add = False
        if proceed_to_add:
            self.children.append(trans)

    def get_first_terminal_child_transitions(self):
        """
        Gets the list of transitions belonging to the first terminal child node of the current tree

        Returns
        ---------
        transitions_list
            List of transitions belonging to the first terminal child node
        """
        if self.children:
            if type(self.children[0]) is ProcessTree:
                return self.children[0].get_first_terminal_child_transitions()
            else:
                return self.children
        return []

    def get_last_terminal_child_transitions(self):
        """
        Gets the list of transitions belonging to the last terminal child node of the current tree

        Returns
        ---------
        transitions_list
            List of transitions belonging to the first terminal child node
        """
        if self.children:
            if type(self.children[-1]) is ProcessTree:
                return self.children[-1].get_last_terminal_child_transitions()
            else:
                return self.children
        return []

    def check_initial_loop(self):
        """
        Check if the tree, on-the-left, starts with a loop

        Returns
        ----------
        boolean
            True if it starts with an initial loop
        """
        if self.children:
            if type(self.children[0]) is ProcessTree:
                if self.children[0].operator == tree_constants.LOOP_OPERATOR:
                    return True
                else:
                    return self.children[0].check_terminal_loop()
        return False

    def check_terminal_loop(self):
        """
        Check if the tree, on-the-right, ends with a loop

        Returns
        -----------
        boolean
            True if it ends with a terminal loop
        """
        if self.children:
            if type(self.children[-1]) is ProcessTree:
                if self.children[-1].operator == tree_constants.LOOP_OPERATOR:
                    return True
                else:
                    return self.children[-1].check_terminal_loop()
        return False

    def check_tau_mandatory_at_initial_marking(self):
        """
        When a conversion to a Petri net is operated, check if is mandatory to add a hidden transition
        at initial marking

        Returns
        ----------
        boolean
            Boolean that is true if it is mandatory to add a hidden transition connecting the initial marking
            to the rest of the process
        """
        condition1 = self.check_initial_loop()
        condition2 = len(self.get_first_terminal_child_transitions()) > 1

        return condition1 or condition2

    def check_tau_mandatory_at_final_marking(self):
        """
        When a conversion to a Petri net is operated, check if is mandatory to add a hidden transition
        at final marking

        Returns
        ----------
        boolean
            Boolean that is true if it is mandatory to add a hidden transition connecting
            the rest of the process to the final marking
        """
        condition1 = self.check_terminal_loop()
        condition2 = len(self.get_last_terminal_child_transitions()) > 1

        return condition1 or condition2


class PTTransition(object):
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

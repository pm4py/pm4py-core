from copy import copy

from pm4py.objects.log.log import TraceLog
from pm4py.objects.process_tree import semantics as pt_sem
from pm4py.objects.process_tree import util as pt_ut


class ProcessTree2(object):

    def __init__(self, operator=None, parent=None, children=None, label=None):
        self._operator = operator
        self._parent = parent
        self._children = list() if children is None else children
        self._label = label

    def _set__operator(self, operator):
        self._operator = operator

    def _set_parent(self, parent):
        self._parent = parent

    def _set_label(self, label):
        self._label = label

    def _get_children(self):
        return self._children

    def _get_parent(self):
        return self._parent

    def _get_operator(self):
        return self._operator

    def _get_label(self):
        return self._label

    def __repr__(self):
        if self.operator is not None:
            rep = str(self._operator) + '( '
            for i in range(0, len(self._children)):
                child = self._children[i]
                rep += str(child) + ', ' if i < len(self._children) - 1 else str(child)
            return rep + ' )'
        elif self.label is not None:
            return self.label
        else:
            return u'\u03c4'

    parent = property(_get_parent, _set_parent)
    children = property(_get_children)
    operator = property(_get_operator)
    label = property(_get_label, _set_label)


if __name__ == '__main__':
    # root = ProcessTree2(operator=pt_opt.Operator2.LOOP)
    # a = ProcessTree2(label='a', parent=root)
    # root.children.append(a)
    # b = ProcessTree2(label=None, parent=root)
    # root.children.append(b)
    # c = ProcessTree2(label='c', parent=root)
    # root.children.append(c)
    tree_str = ' ->( X( \'a\',\'b\', tau), + (\'c\',\'d\') )'
    tree = pt_ut.parse(tree_str)
    execution_sequence = pt_sem.execute(tree)
    print(execution_sequence)
    print(pt_ut.project_execution_sequence_to_leafs(execution_sequence))
    print(pt_ut.project_execution_sequence_to_labels(execution_sequence))
    # print(list(execution_sequence))


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

        self.node_object = None

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

    def set_operator(self, operator):
        """
        Set operator for the current subtree

        Parameters
        -----------
        operator
            Operator to set
        """
        self.operator = operator

        self.node_object = tree_constants.MAPPING[self.operator](self)

    def generate_trace(self):
        """
        Generate a trace out of the current process tree

        Returns
        ---------
        trace
            Trace of trace log object
        """
        this_rec_depth = copy(self.rec_depth)
        self.rec_depth = 0
        concurrent_trace = ConcurrentTrace()
        self.node_object.generate_events_trace(concurrent_trace)
        trace = concurrent_trace.get_trace()
        self.rec_depth = this_rec_depth
        return trace

    def generate_log(self, no_traces=100):
        """
        Generate a log with the given number of traces from the current process tree

        Returns
        ----------
        log
            Trace log whose traces follow the process tree
        """
        log = TraceLog()

        for i in range(no_traces):
            log.append(self.generate_trace())

        return log

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

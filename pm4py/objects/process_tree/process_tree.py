from pm4py.objects.process_tree import pt_operator


class ProcessTree(object):

    def __init__(self, operator=None, parent=None, children=None, label=None):
        """
        Constructor

        Parameters
        ------------
        operator
            Operator (of the current node) of the process tree
        parent
            Parent node (of the current node)
        children
            List of children of the current node
        label
            Label (of the current node)
        """
        self._operator = operator
        self._parent = parent
        self._children = list() if children is None else children
        self._label = label

    def __hash__(self):
        if self.label is not None:
            return hash(self.label)
        elif len(self.children) == 0:
            return 37
        else:
            h = 1337
            for i in range(len(self.children)):
                h += 41 * i * hash(self.children[i])
            if self.operator == pt_operator.Operator.SEQUENCE:
                h = h * 13
            elif self.operator == pt_operator.Operator.XOR:
                h = h * 17
            elif self.operator == pt_operator.Operator.OR:
                h = h * 23
            elif self.operator == pt_operator.Operator.PARALLEL:
                h = h * 29
            elif self.operator == pt_operator.Operator.LOOP:
                h = h * 37
            return h % 268435456

    def _set_operator(self, operator):
        self._operator = operator

    def _set_parent(self, parent):
        self._parent = parent

    def _set_label(self, label):
        self._label = label

    def _set_children(self, children):
        self._children = children

    def _get_children(self):
        return self._children

    def _get_parent(self):
        return self._parent

    def _get_operator(self):
        return self._operator

    def _get_label(self):
        return self._label

    def __eq__(self, other):
        if self.label is not None:
            return True if other.label == self.label else False
        elif len(self.children) == 0:
            return other.label is None and len(other.children) == 0
        else:
            if self.operator == other.operator:
                if len(self.children) != len(other.children):
                    return False
                else:
                    for i in range(len(self.children)):
                        if self.children[i] != other.children[i]:
                            return False
                    return True
            else:
                return False

    def __repr__(self):
        """
        Returns a string representation of the process tree

        Returns
        ------------
        stri
            String representation of the process tree
        """
        if self.operator is not None:
            rep = str(self._operator) + '( '
            for i in range(0, len(self._children)):
                child = self._children[i]
                if len(child.children) == 0:
                    if child.label is not None:
                        rep += '\'' + str(child) + '\'' + ', ' if i < len(self._children) - 1 else '\'' + str(
                            child) + '\''
                    else:
                        rep += str(child) + ', ' if i < len(self._children) - 1 else str(child)
                else:
                    rep += str(child) + ', ' if i < len(self._children) - 1 else str(child)
            return rep + ' )'
        elif self.label is not None:
            return self.label
        else:
            return u'\u03c4'

    def __str__(self):
        """
        Returns a string representation of the process tree

        Returns
        ------------
        stri
            String representation of the process tree
        """
        return self.__repr__()

    def _get_root(self):
        root = self
        while root._get_parent() is not None:
            root = root._get_parent()
        return root

    def _get_leaves(self):
        root = self._get_root()
        leaves = root
        if root._get_children != list():
            leaves = root._get_children()
            change_of_leaves = True
            while change_of_leaves:
                leaves_to_replace = list()
                new_leaves = list()
                for leaf in leaves:
                    if leaf._get_children() != list():
                        leaves_to_replace.append(leaf)
                    else:
                        new_leaves.append(leaf)
                if leaves_to_replace != list():
                    for leaf in leaves_to_replace:
                        for el in leaf.children:
                            new_leaves.append(el)
                    leaves = new_leaves
                else:
                    change_of_leaves = False
        return leaves

    def _print_tree(self):
        root = self._get_root()
        print(root)

    parent = property(_get_parent, _set_parent)
    children = property(_get_children, _set_children)
    operator = property(_get_operator, _set_operator)
    label = property(_get_label, _set_label)

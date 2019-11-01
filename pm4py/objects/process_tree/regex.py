import re
from pm4py.objects.process_tree import pt_operator
import itertools


def get_new_char(label, shared_obj):
    """
    Get a new single character describing the activity, for the regex

    Parameters
    ------------
    label
        Label of the transition
    shared_obj
        Shared object
    """
    list_to_avoid = ["[", "]", "(", ")", "*", "+", "^", "?", "\r", "\n", " ", "\t", "$", "\"", "!", "#", "&", "%", "|",
                     ".", ",", ";", "-", "'", "\\", "/", "{", "}"]
    shared_obj.count_char = shared_obj.count_char + 1
    while chr(shared_obj.count_char) in list_to_avoid:
        shared_obj.count_char = shared_obj.count_char + 1
    shared_obj.mapping_dictio[label] = chr(shared_obj.count_char)


class SharedObj:
    def __init__(self):
        self.mapping_dictio = None
        if self.mapping_dictio is None:
            self.mapping_dictio = {}
        self.count_char = 0


def pt_to_regex(tree, rec_depth=0, shared_obj=None, parameters=None):
    """
    Transforms a process tree to a regular expression

    NB: The conversion is not yet working with trees containing an AND and/or an OR operator!

    Parameters
    ------------
    tree
        Process tree
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    if shared_obj is None:
        shared_obj = SharedObj()

    stru = ""

    if tree.operator is not None:
        contains_tau = len(list(child for child in tree.children if child.operator is None and child.label is None)) > 0
        children_rep = []
        for child in tree.children:
            rep, shared_obj = pt_to_regex(child, rec_depth=rec_depth + 1, shared_obj=shared_obj, parameters=parameters)
            children_rep.append(rep)
        if tree.operator == pt_operator.Operator.SEQUENCE:
            children_rep = [x for x in children_rep if not x is None]
            stru = "(" + "".join(children_rep) + ")"
        elif tree.operator == pt_operator.Operator.XOR:
            children_rep = [x for x in children_rep if not x is None]
            stru = "(" + "|".join(children_rep) + ")"
            if contains_tau:
                stru = "(" + stru + "?)"
        elif tree.operator == pt_operator.Operator.LOOP:
            children_rep = [x for x in children_rep if not x is None]
            if len(children_rep) == 1:
                stru = "(" + children_rep[0] + ")+"
            else:
                stru = "(" + "".join(children_rep) + ")*" + children_rep[0]
        elif tree.operator == pt_operator.Operator.PARALLEL:
            raise Exception("the conversion is not yet working with trees containing an AND and/or an OR operator!")
        elif tree.operator == pt_operator.Operator.OR:
            raise Exception("the conversion is not yet working with trees containing an AND and/or an OR operator!")

    elif tree.label is not None:
        if tree.label not in shared_obj.mapping_dictio:
            get_new_char(tree.label, shared_obj)
        stru = shared_obj.mapping_dictio[tree.label]
    elif tree.label is None:
        return None, shared_obj

    if rec_depth == 0:
        ret = "^" + stru + "?", shared_obj.mapping_dictio
        #print(ret)
        return ret

    return stru, shared_obj

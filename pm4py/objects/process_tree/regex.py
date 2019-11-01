import re
from pm4py.objects.process_tree import pt_operator
import itertools

def get_new_char(label, mapping_dictio, count_char):
    """
    Get a new single character describing the activity, for the regex

    Parameters
    ------------
    label
        Label of the transition
    mapping_dictio
        Mapping dictionary
    count_char
        Count character
    """
    list_to_avoid = ["[", "]", "(", ")", "*", "+", "^", "?"]
    count_char = count_char + 1
    while chr(count_char) in list_to_avoid:
        count_char = count_char + 1
    mapping_dictio[label] = chr(count_char)
    return mapping_dictio, count_char

class SharedObj:
    def __init__(self):
        self.mapping_dictio=None
        if self.mapping_dictio is None:
            self.mapping_dictio = {}
        self.count_char = 0

def pt_to_regex(tree, rec_depth=0, shared_obj=None, parameters=None):
    """
    Transforms a process tree to a regular expression

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
            rep, shared_obj = pt_to_regex(child, rec_depth=rec_depth+1, shared_obj=shared_obj, parameters=parameters)
            children_rep.append(rep)
        if tree.operator == pt_operator.Operator.SEQUENCE:
            children_rep = [x for x in children_rep if not x is None]
            stru = "([" + "".join(children_rep) + "])"
        elif tree.operator == pt_operator.Operator.XOR:
            children_rep = [x for x in children_rep if not x is None]
            stru = "(" + "|".join(children_rep) + ")"
            if contains_tau:
                stru = "(" + stru + "?)"
        elif tree.operator == pt_operator.Operator.LOOP:
            children_rep = [x for x in children_rep if not x is None]
            if len(children_rep) == 1:
                stru = "(("+children_rep[0]+")+)"
            else:
                stru = "(("+"".join(children_rep)+")*"+children_rep[0]+")"
        elif tree.operator == pt_operator.Operator.PARALLEL:
            children_rep = [x for x in children_rep if not x is None]
            stru_list = ["("]

            permutations = list(itertools.permutations(children_rep))
            for index, p in enumerate(permutations):
                if index > 0:
                    stru_list.append("|")
                stru_list.append("(" + "".join(p) + ")")

            stru_list.append(")")
            stru = "".join(stru_list)
        elif tree.operator == pt_operator.Operator.OR:
            raise Exception("not implemented yet!")

    elif tree.label is not None:
        if tree.label not in shared_obj.mapping_dictio:
            mapping_dictio, count_char = get_new_char(tree.label, shared_obj.mapping_dictio, shared_obj.count_char)
        stru = mapping_dictio[tree.label]
    elif tree.label is None:
        return None

    if rec_depth == 0:
        return "^" + stru + "?", shared_obj.mapping_dictio

    return stru, shared_obj

import re

def check_reg_matching(reg, stru):
    """
    Check if a regular expression matches a given string

    Parameters
    -------------
    reg
        Regular expression
    stru
        String

    Returns
    -------------
    boolean
        Matches or not?
    """
    if type(reg) is str:
        reg = re.compile(reg)

    match = re.match(reg, stru)

    if match is not None:
        stru = str(match)
        if "match='" in stru:
            stru = str(match).split("match='")[1].split("'")[0]
        elif "match=\"" in stru:
            stru = str(match).split("match=\"")[1].split("\"")[0]
        else:
            raise Exception("match not contained in the match")
        if len(stru) == 0:
            return False
        return True
    else:
        return False

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

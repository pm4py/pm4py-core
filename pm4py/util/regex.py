'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import re

def check_reg_matching(reg, stringa):
    """
    Check if a regular expression matches a given string

    Parameters
    -------------
    reg
        Regular expression
    stringa
        String

    Returns
    -------------
    boolean
        Matches or not?
    """
    if type(reg) is str:
        reg = re.compile(reg)

    match = re.match(reg, stringa)

    if match is not None:
        stru = str(match)
        if "match='" in stru:
            stru = str(match).split("match='")[1].split("'")[0]
        elif "match=\"" in stru:
            stru = str(match).split("match=\"")[1].split("\"")[0]
        else:
            raise Exception("match not contained in the match")
        if len(stru) == 0:
            #print(stru, stringa)
            #print(len(stru), len(stringa))
            #input()

            return False
        return True
    else:
        return False


def regex_replace_mapping(reg_stri, mapping, special_char="@@", parameters=None):
    """
    Replace strings in a regex given the mapping

    Parameters
    -------------
    reg_stri
        Regex string
    mapping
        Mapping
    special_char
        Specification of the special character
    parameters
        Parameters of the algorithm

    Returns
    ------------
    reg
        Compiled Regex where the elements where replaced according to the mapping
    """
    if parameters is None:
        parameters = {}

    splitting = reg_stri.split(special_char)
    for i in range(len(splitting)):
        if splitting[i] in mapping:
            splitting[i] = mapping[splitting[i]]

    reg_stri = "".join(splitting)
    reg = re.compile(reg_stri)

    return reg

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
                     ".", ",", ";", "-", "'", "\\", "/", "{", "}", "$"]
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

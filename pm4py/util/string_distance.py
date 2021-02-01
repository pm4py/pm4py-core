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
import sys
from typing import List, Union

import stringdist

levenshtein = lambda stru1, stru2: stringdist.levenshtein(stru1, stru2)


def argmin_levenshtein(stru: str, list_stri: List[str]) -> Union[str, None]:
    """
    Given a string (stru), finds a string in a list
    of strings (list_stri) that minimizes the Levenshtein distance.

    Parameters
    --------------
    stru
         String (that is compared)
    list_stri
        List of comparison strings

    Returns
    --------------
    argmin_dist
        String (belonging to list_stri) that minimizes the Levenshtein distance
        with the 'stru' argument
    """
    if list_stri:
        len_stru = len(stru)
        argmin_dist = None
        min_edit_dist = sys.maxsize
        # sort the strings in the list based on the actual length in comparison
        # to the provided string
        list_stri = sorted(list_stri, key=lambda x: abs(len(x) - len_stru))
        for comp_stri in list_stri:
            this_length_diff = abs(len(comp_stri) - len_stru)
            # to make things faster, breaks whether we reach a string
            # which distance is greater or equal than the edit distance
            # with a previous string, because the edit distance would then
            # be trivially greater or equal in length
            if this_length_diff >= min_edit_dist:
                break
            dist_this_comp = levenshtein(stru, comp_stri)
            if dist_this_comp < min_edit_dist:
                argmin_dist = comp_stri
                min_edit_dist = dist_this_comp
        return argmin_dist
    return None


def argmax_levenshtein(stru: str, list_stri: List[str]) -> Union[str, None]:
    """
    Given a string (stru), finds a string in a list
    of strings (list_stri) that maximizes the Levenshtein distance.

    Parameters
    --------------
    stru
         String (that is compared)
    list_stri
        List of comparison strings

    Returns
    --------------
    argmax_dist
        String (belonging to list_stri) that maximizes the Levenshtein distance
        with the 'stru' argument
    """
    if list_stri:
        len_stru = len(stru)
        argmax_dist = None
        max_edit_dist = 0
        # sort the strings in the list based on the actual length in comparison
        # to the provided string
        list_stri = sorted(list_stri, key=lambda x: -len(x))
        for comp_stri in list_stri:
            # to make things faster, breaks whether the
            # following condition is reached
            if len(comp_stri) + len_stru <= max_edit_dist:
                break
            dist_this_comp = levenshtein(stru, comp_stri)
            if dist_this_comp > max_edit_dist:
                argmax_dist = comp_stri
                max_edit_dist = dist_this_comp
        return argmax_dist
    return None

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
from pm4py.util.regex import SharedObj, get_new_char
from pm4py.util import string_distance
import numpy as np
from pyemd import emd
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, List


class Parameters:
    STRING_DISTANCE = "string_distance"


def normalized_levensthein(s1, s2):
    """
    Normalized Levensthein distance

    Parameters
    -------------
    s1
        First string
    s2
        Second string

    Returns
    --------------
    dist
        Distance
    """
    return float(string_distance.levenshtein(s1, s2)) / float(max(len(s1), len(s2)))


def get_act_correspondence(activities, parameters=None):
    """
    Gets an encoding for each activity

    Parameters
    --------------
    activities
        Activities of the two languages
    parameters
        Parameters

    Returns
    -------------
    encoding
        Encoding into hex characters
    """
    if parameters is None:
        parameters = {}

    shared_obj = SharedObj()
    ret = {}
    for act in activities:
        get_new_char(act, shared_obj)
        ret[act] = shared_obj.mapping_dictio[act]

    return ret


def encode_two_languages(lang1, lang2, parameters=None):
    """
    Encode the two languages into hexadecimal strings

    Parameters
    --------------
    lang1
        Language 1
    lang2
        Language 2
    parameters
        Parameters of the algorithm

    Returns
    --------------
    enc1
        Encoding of the first language
    enc2
        Encoding of the second language
    """
    if parameters is None:
        parameters = {}

    all_activities = sorted(list(set(y for x in lang1 for y in x).union(set(y for x in lang2 for y in x))))
    acts_corresp = get_act_correspondence(all_activities, parameters=parameters)

    enc1 = {}
    enc2 = {}

    for k in lang1:
        new_key = "".join(acts_corresp[i] for i in k)
        enc1[new_key] = lang1[k]

    for k in lang2:
        new_key = "".join(acts_corresp[i] for i in k)
        enc2[new_key] = lang2[k]

    # each language should have the same keys, even if not present
    for x in enc1:
        if x not in enc2:
            enc2[x] = 0.0

    for x in enc2:
        if x not in enc1:
            enc1[x] = 0.0

    enc1 = [(x, y) for x, y in enc1.items()]
    enc2 = [(x, y) for x, y in enc2.items()]

    # sort the keys in a decreasing way
    enc1 = sorted(enc1, reverse=True, key=lambda x: x[0])
    enc2 = sorted(enc2, reverse=True, key=lambda x: x[0])

    return enc1, enc2


def apply(lang1: Dict[List[str], float], lang2: Dict[List[str], float], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    Calculates the EMD distance between the two stochastic languages

    Parameters
    -------------
    lang1
        First language
    lang2
        Second language
    parameters
        Parameters of the algorithm, including:
            - Parameters.STRING_DISTANCE: function that accepts two strings and returns a distance

    Returns
    ---------------
    emd_dist
        EMD distance
    """
    if parameters is None:
        parameters = {}

    distance_function = exec_utils.get_param_value(Parameters.STRING_DISTANCE, parameters, normalized_levensthein)

    enc1, enc2 = encode_two_languages(lang1, lang2, parameters=parameters)

    # transform everything into a numpy array
    first_histogram = np.array([x[1] for x in enc1])
    second_histogram = np.array([x[1] for x in enc2])

    # including a distance matrix that includes the distance between
    # the traces
    distance_matrix = []
    for x in enc1:
        distance_matrix.append([])
        for y in enc2:
            # calculates the (normalized) distance between the strings
            dist = distance_function(x[0], y[0])
            distance_matrix[-1].append(float(dist))

    distance_matrix = np.array(distance_matrix)

    ret = emd(first_histogram, second_histogram, distance_matrix)

    return ret

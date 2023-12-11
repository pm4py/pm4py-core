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

from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils, pandas_utils


class Parameters(Enum):
    PREFIX_OR_SUFFIX = "prefix_or_suffix"
    INDEX_ATTRIBUTE = "index_attribute"
    LEFT_SUFFIX = "left_suffix"
    RIGHT_SUFFIX = "right_suffix"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Gets for each event and each one of the related objects,
    the prefix or the suffix.
    E.g. if there is an object "o1" with lifecycle "e1", "e2", "e3",
    then:

    The prefix of "e1" for "o1" is empty.
    The prefix of "e2" for "o1" is ["e1"].
    The prefix of "e3" for "o1" is ["e1", "e2"].

    The suffix of "e1" for "o1" is ["e2", "e3"].
    The suffix of "e2" for "o1" is ["o3"].
    The suffix of "e3" for "o1" is empty.

    Parameters
    --------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
            - Parameters.PREFIX_OR_SUFFIX => establishes if the prefix or the suffix of the event per object is
                                                needed. Possible values:
                                                    - "prefix"
                                                    - "suffix"
            - Parameters.INDEX_ATTRIBUTE => the index attribute which is artificially inserted in the relations df.
            - Parameters.LEFT_SUFFIX => the suffix for the left-part of the merge.
            - Parameters.RIGHT_SUFFIX => the suffix for the right-part of the merge

    Returns
    --------------
    ret
        A dictionary where the first key is the event, the second key is the object, and the value is a list
        of events which are the object-specific prefix or suffix of the event.
    """
    if parameters is None:
        parameters = {}

    prefix_or_suffix = exec_utils.get_param_value(Parameters.PREFIX_OR_SUFFIX, parameters, "prefix")
    index_attribute = exec_utils.get_param_value(Parameters.INDEX_ATTRIBUTE, parameters, "@@index")
    left_suffix = exec_utils.get_param_value(Parameters.LEFT_SUFFIX, parameters, "_LEFT")
    right_suffix = exec_utils.get_param_value(Parameters.RIGHT_SUFFIX, parameters, "_RIGHT")

    relations = ocel.relations.copy()
    relations = pandas_utils.insert_index(relations, index_attribute, reset_index=False, copy_dataframe=False)
    relations_merged = relations.merge(relations, left_on=ocel.object_id_column, right_on=ocel.object_id_column, suffixes=(left_suffix, right_suffix))
    if prefix_or_suffix == "prefix":
        relations_merged = relations_merged[
            relations_merged[index_attribute + left_suffix] > relations_merged[index_attribute + right_suffix]]
    else:
        relations_merged = relations_merged[
            relations_merged[index_attribute + left_suffix] < relations_merged[index_attribute + right_suffix]]
    relations_merged = relations_merged[[ocel.event_id_column+left_suffix, ocel.event_id_column+right_suffix, ocel.object_id_column]]
    relations_merged = relations_merged[relations_merged[ocel.event_id_column+left_suffix] != relations_merged[ocel.event_id_column+right_suffix]]
    relations_merged = relations_merged.to_dict('records')

    ret = {}
    for el in relations_merged:
        e1 = el[ocel.event_id_column+left_suffix]
        e2 = el[ocel.event_id_column+right_suffix]
        obj = el[ocel.object_id_column]
        if e1 not in ret:
            ret[e1] = {}
        if obj not in ret[e1]:
            ret[e1][obj] = []
        if e2 not in ret[e1][obj]:
            ret[e1][obj].append(e2)

    return ret

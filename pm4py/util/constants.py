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
PARAMETER_CONSTANT_ACTIVITY_KEY = 'pm4py:param:activity_key'
PARAMETER_CONSTANT_ATTRIBUTE_KEY = "pm4py:param:attribute_key"
PARAMETER_CONSTANT_TIMESTAMP_KEY = 'pm4py:param:timestamp_key'
PARAMETER_CONSTANT_START_TIMESTAMP_KEY = 'pm4py:param:start_timestamp_key'
PARAMETER_CONSTANT_CASEID_KEY = 'case_id_glue'
PARAMETER_CONSTANT_RESOURCE_KEY = 'pm4py:param:resource_key'
PARAMETER_CONSTANT_TRANSITION_KEY = 'pm4py:param:transition_key'
PARAMETER_CONSTANT_GROUP_KEY = 'pm4py:param:group_key'

GROUPED_DATAFRAME = 'grouped_dataframe'
RETURN_EA_COUNT_DICT_AUTOFILTER = 'return_ea_count_dict_autofilter'
PARAM_MOST_COMMON_VARIANT = "most_common_variant"
PARAM_MOST_COMMON_PATHS = "most_common_paths"

CASE_CONCEPT_NAME = "case:concept:name"
CASE_ATTRIBUTE_GLUE = 'case:concept:name'
CASE_ATTRIBUTE_PREFIX = 'case:'

# the following can be removed
PARAMETER_KEY_CASE_GLUE = 'case_id_glue'
PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX = 'case:'

STOCHASTIC_DISTRIBUTION = "stochastic_distribution"
LAYOUT_INFORMATION_PETRI = "layout_information_petri"
PLACE_NAME_TAG = "place_name_tag"
TRANS_NAME_TAG = "trans_name_tag"

DEFAULT_VARIANT_SEP = ","
DEFAULT_INDEX_KEY = "@@index"
DEFAULT_INDEX_IN_TRACE_KEY = "@@index_in_trace"
DEFAULT_EVENT_INDEX_KEY = "@@event_index"
DEFAULT_FLOW_TIME = "@@flow_time"
DEFAULT_CLASSIFIER_ATTRIBUTE = "@@classifier"

DEFAULT_ENCODING = "utf-8"

from enum import Enum


class AvailableSerializations(Enum):
    EVENT_LOG = "event_log"
    DATAFRAME = "dataframe"
    PETRI_NET = "petri_net"
    PROCESS_TREE = "process_tree"
    BPMN = "bpmn"
    DFG = "dfg"

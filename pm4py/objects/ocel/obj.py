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
from enum import Enum

import pandas as pd

from pm4py.objects.ocel import constants
from pm4py.util import exec_utils
import pandas as pd


class Parameters(Enum):
    EVENT_ID = constants.PARAM_EVENT_ID
    EVENT_ACTIVITY = constants.PARAM_EVENT_ACTIVITY
    EVENT_TIMESTAMP = constants.PARAM_EVENT_TIMESTAMP
    OBJECT_ID = constants.PARAM_OBJECT_ID
    OBJECT_TYPE = constants.PARAM_OBJECT_TYPE


class OCEL(object):
    def __init__(self, events=None, objects=None, relations=None, globals=None, parameters=None):
        if events is None:
            events = pd.DataFrame()
        if objects is None:
            objects = pd.DataFrame()
        if relations is None:
            relations = pd.DataFrame()
        if globals is None:
            globals = {}
        if parameters is None:
            parameters = {}

        self.events = events
        self.objects = objects
        self.relations = relations
        self.globals = globals

        self.event_id_column = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, constants.DEFAULT_EVENT_ID)
        self.object_id_column = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, constants.DEFAULT_OBJECT_ID)
        self.object_type_column = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters,
                                                             constants.DEFAULT_OBJECT_TYPE)

        self.event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters,
                                                         constants.DEFAULT_EVENT_ACTIVITY)
        self.event_timestamp = exec_utils.get_param_value(Parameters.EVENT_TIMESTAMP, parameters,
                                                          constants.DEFAULT_EVENT_TIMESTAMP)

    def get_extended_table(self, ot_prefix=constants.DEFAULT_OBJECT_TYPE_PREFIX_EXTENDED) -> pd.DataFrame:
        """
        Transforms the current OCEL data structure into a Pandas dataframe containing the events with their
        attributes and the related objects per object type.
        """
        object_types = self.relations[self.object_type_column].unique()
        table = self.events.copy().set_index(self.event_id_column)
        for ot in object_types:
            table[ot_prefix + ot] = \
                self.relations[self.relations[self.object_type_column] == ot].groupby(self.event_id_column)[
                    self.object_id_column].apply(list)
        table = table.reset_index()
        return table

    def get_summary(self) -> str:
        """
        Gets a string summary of the object-centric event log
        """
        ret = []
        ret.append("Object-Centric Event Log (")
        ret.append("number of events: %d" % (len(self.events)))
        ret.append(", number of objects: %d" % (len(self.objects)))
        ret.append(", number of activities: %d" % (self.events[self.event_activity].nunique()))
        ret.append(", number of object types: %d" % (self.objects[self.object_type_column].nunique()))
        ret.append(", events-objects relationships: %d)" % (len(self.relations)))
        ret.append("\n")
        ret.append("Activities occurrences: " + str(self.events[self.event_activity].value_counts().to_dict()))
        ret.append("\n")
        ret.append("Object types occurrences: " + str(self.objects[self.object_type_column].value_counts().to_dict()))
        ret.append("\n")
        ret.append(
            "Please use <THIS>.get_extended_table() to get a dataframe representation of the events related to the objects.")
        return "".join(ret)

    def __str__(self):
        return str(self.get_summary())

    def __repr__(self):
        return str(self.get_summary())

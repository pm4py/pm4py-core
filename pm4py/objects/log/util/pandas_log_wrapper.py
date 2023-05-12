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
import pandas as pd
from typing import Optional, Dict, Any
from pm4py.util import constants, exec_utils
from enum import Enum
from collections.abc import Sequence


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    CASE_ATTRIBUTE_PREFIX = constants.CASE_ATTRIBUTE_PREFIX


class PandasTraceWrapper(Sequence):
    def __init__(self, dataframe: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None):
        if parameters is None:
            parameters = {}

        self.parameters = parameters
        self.dataframe = dataframe
        self.case_attribute_prefix = exec_utils.get_param_value(Parameters.CASE_ATTRIBUTE_PREFIX, parameters,
                                                                constants.CASE_ATTRIBUTE_PREFIX)

        self.attributes = self.dataframe.loc[0].to_dict()
        self.attributes = {x.split(self.case_attribute_prefix)[-1]: y for x, y in self.attributes.items() if
                           x.startswith(self.case_attribute_prefix)}

    def __getitem__(self, key):
        if type(key) is slice:
            start = key.start % len(self.dataframe)
            stop = key.stop % len(self.dataframe)
            sli = slice(start, stop - 1, key.step)
            return self.dataframe.loc[sli].to_dict("records")
        key = key % len(self.dataframe)
        return self.dataframe.loc[key].to_dict()

    def __iter__(self):
        return iter(self.dataframe.to_dict('records'))

    def __len__(self):
        return len(self.dataframe)

    def _get_list(self):
        return self.dataframe.to_dict('records')

    _list = property(_get_list)


class PandasLogWrapper(Sequence):
    # permits to iterate over a Pandas dataframe and access its Traces object *without* a conversion to EventLog
    def __init__(self, dataframe: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None):
        if parameters is None:
            parameters = {}

        self.parameters = parameters
        self.case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
        self.dataframe = dataframe

        self.grouped_dataframe = self.dataframe.groupby(self.case_id_key).groups
        self.keys = list(self.grouped_dataframe)

        self.attributes = {}
        self.extensions = {}
        self.omni_present = {}
        self.classifiers = {}
        self.properties = {}

    def __getitem__(self, key):
        if type(key) is slice:
            start = key.start % len(self.dataframe)
            stop = key.stop % len(self.dataframe)
            sli = slice(start, stop, key.step)
            ret = []
            for x in self.keys[sli]:
                ret.append(PandasTraceWrapper(self.dataframe.loc[self.grouped_dataframe[x]].copy().reset_index(),
                                  parameters=self.parameters))
            return ret
        key = key % len(self.grouped_dataframe)
        return PandasTraceWrapper(self.dataframe.loc[self.grouped_dataframe[self.keys[key]]].copy().reset_index(),
                                  parameters=self.parameters)

    def __iter__(self):
        for key in self.keys:
            yield PandasTraceWrapper(self.dataframe.loc[self.grouped_dataframe[key]].copy().reset_index(),
                                     parameters=self.parameters)

    def __len__(self):
        return len(self.grouped_dataframe)

    def _get_list(self):
        ret = []
        for key in self.keys:
            ret.append(PandasTraceWrapper(self.dataframe.loc[self.grouped_dataframe[key]].copy().reset_index(),
                                     parameters=self.parameters))
        return ret

    _list = property(_get_list)

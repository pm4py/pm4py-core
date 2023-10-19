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
from pm4py.util import constants, exec_utils
from io import StringIO
from enum import Enum


class Parameters(Enum):
    ENCODING = "encoding"


def import_dfg_from_rows(rows, parameters=None):
    """
    Import a DFG (along with the start and end activities) from the rows of a .dfg file

    Parameters
    --------------
    rows
        Rows the DFG file
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    if parameters is None:
        parameters = {}

    activities = []
    start_activities = {}
    end_activities = {}
    dfg = {}

    num_activities = int(rows[0])
    i = 1
    while i <= num_activities:
        activities.append(rows[i].strip())
        i = i + 1

    num_sa = int(rows[i])

    target = i + num_sa
    i = i + 1

    while i <= target:
        act, count = rows[i].strip().split("x")
        act = activities[int(act)]
        count = int(count)
        start_activities[act] = count
        i = i + 1

    num_ea = int(rows[i])

    target = i + num_ea
    i = i + 1

    while i <= target:
        act, count = rows[i].strip().split("x")
        act = activities[int(act)]
        count = int(count)
        end_activities[act] = count
        i = i + 1

    while i < len(rows):
        acts, count = rows[i].strip().split("x")
        count = int(count)
        a1, a2 = acts.split(">")
        a1 = activities[int(a1)]
        a2 = activities[int(a2)]
        dfg[(a1, a2)] = count
        i = i + 1

    return dfg, start_activities, end_activities


def apply(file_path, parameters=None):
    """
    Import a DFG (along with the start and end activities) from a .dfg file

    Parameters
    --------------
    file_path
        Path of the DFG file
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)

    F = open(file_path, "r", encoding=encoding)
    content = F.readlines()
    F.close()

    return import_dfg_from_rows(content, parameters=parameters)


def import_dfg_from_string(dfg_string, parameters=None):
    """
    Import a DFG (along with the start and end activities) from a string representing a .dfg file

    Parameters
    --------------
    dfg_string
        String representing a .dfg file
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)

    if type(dfg_string) is bytes:
        dfg_string = dfg_string.decode(encoding)

    return import_dfg_from_rows(StringIO(dfg_string).readlines(), parameters=parameters)

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
from pm4py.util import exec_utils
from enum import Enum
from collections import Counter
from pm4py.objects.dfg.utils import dfg_utils
from pm4py.util import constants


class Parameters(Enum):
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"
    ENCODING = "encoding"


def export_line_by_line(dfg, parameters=None):
    """
    Exports a DFG into the .dfg format
    - Line by line yielding

    Parameters
    --------------
    dfg
        DFG
    parameters
        Parameters of the algorithm

    Returns
    --------------
    line
        Lines of the .dfg file (yielded one-by-one)
    """
    if parameters is None:
        parameters = {}

    start_activities = exec_utils.get_param_value(Parameters.START_ACTIVITIES, parameters,
                                                  Counter(dfg_utils.infer_start_activities(dfg)))
    end_activities = exec_utils.get_param_value(Parameters.END_ACTIVITIES, parameters,
                                                Counter(dfg_utils.infer_end_activities(dfg)))

    if len(start_activities) == 0:
        raise Exception(
            "error: impossible to determine automatically the start activities from the DFG. Please specify them manually through the START_ACTIVITIES parameter")

    if len(end_activities) == 0:
        raise Exception(
            "error: impossible to determine automatically the end activities from the DFG. Please specify them manually through the END_ACTIVITIES parameter")

    activities = list(set(x[0] for x in dfg).union(set(x[1] for x in dfg)))

    yield "%d\n" % (len(activities))
    for act in activities:
        yield "%s\n" % (act)

    yield "%d\n" % (len(start_activities))
    for act, count in start_activities.items():
        yield "%dx%d\n" % (activities.index(act), count)

    yield "%d\n" % (len(end_activities))
    for act, count in end_activities.items():
        yield "%dx%d\n" % (activities.index(act), count)

    for el, count in dfg.items():
        yield "%d>%dx%d\n" % (activities.index(el[0]), activities.index(el[1]), count)


def apply(dfg, output_path, parameters=None):
    """
    Exports a DFG into a .dfg file

    Parameters
    ----------------
    dfg
        Directly-Follows Graph
    output_path
        Output path
    parameters
        Parameters of the algorithm, including:
            Parameters.START_ACTIVITIES => Start activities of the DFG
            Parameters.END_ACTIVITIES => End activities of the DFG
            Parameters.ENCODING => The encoding to be used (default: utf-8)
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)

    F = open(output_path, "wb")
    for row in export_line_by_line(dfg, parameters=parameters):
        F.write(row.encode(encoding))
    F.close()


def export_as_string(dfg, parameters=None):
    """
    Exports a DFG as a string

    Parameters
    --------------
    dfg
        Directly-Follows Graph
    parameters
        Parameters of the algorithm, including:
            Parameters.START_ACTIVITIES => Start activities of the DFG
            Parameters.END_ACTIVITIES => End activities of the DFG
            Parameters.ENCODING => The encoding to be used (default: utf-8)

    Returns
    --------------
    binary_string
        Binary string
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)

    ret = []
    for row in export_line_by_line(dfg, parameters=parameters):
        ret.append(row)
    ret = "".join(ret)
    ret = ret.encode(encoding)

    return ret

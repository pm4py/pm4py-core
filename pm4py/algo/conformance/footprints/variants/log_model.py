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
from pm4py.util import exec_utils, xes_constants, constants
from pm4py.algo.discovery.footprints.outputs import Outputs


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    STRICT = "strict"


def apply_single(log_footprints, model_footprints, parameters=None):
    """
    Apply footprints conformance between a log footprints object
    and a model footprints object

    Parameters
    -----------------
    log_footprints
        Footprints of the log (NOT a list, but a single footprints object)
    model_footprints
        Footprints of the model
    parameters
        Parameters of the algorithm, including:
            - Parameters.STRICT => strict check of the footprints

    Returns
    ------------------
    violations
        Set of all the violations between the log footprints
        and the model footprints
    """
    if parameters is None:
        parameters = {}

    strict = exec_utils.get_param_value(Parameters.STRICT, parameters, False)

    if strict:
        s1 = log_footprints[Outputs.SEQUENCE.value].difference(model_footprints[Outputs.SEQUENCE.value])
        s2 = log_footprints[Outputs.PARALLEL.value].difference(model_footprints[Outputs.PARALLEL.value])

        violations = s1.union(s2)

    else:
        s1 = log_footprints[Outputs.SEQUENCE.value].union(log_footprints[Outputs.PARALLEL.value])
        s2 = model_footprints[Outputs.SEQUENCE.value].union(model_footprints[Outputs.PARALLEL.value])

        violations = s1.difference(s2)

    return violations


def apply(log_footprints, model_footprints, parameters=None):
    """
    Apply footprints conformance between a log footprints object
    and a model footprints object

    Parameters
    -----------------
    log_footprints
        Footprints of the log
    model_footprints
        Footprints of the model
    parameters
        Parameters of the algorithm, including:
            - Parameters.STRICT => strict check of the footprints

    Returns
    ------------------
    violations
        Set of all the violations between the log footprints
        and the model footprints, OR list of case-per-case violations
    """
    if type(log_footprints) is list:
        ret = []
        for case_footprints in log_footprints:
            ret.append(apply_single(case_footprints, model_footprints, parameters=parameters))
        return ret
    return apply_single(log_footprints, model_footprints, parameters=parameters)


def get_diagnostics_dataframe(log, conf_result, parameters=None):
    """
    Gets the diagnostics dataframe from the log
    and the results of footprints conformance checking
    (trace-by-trace)

    Parameters
    --------------
    log
        Event log
    conf_result
        Conformance checking results (trace-by-trace)

    Returns
    --------------
    diagn_dataframe
        Diagnostics dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)

    import pandas as pd

    diagn_stream = []

    for index in range(len(log)):
        case_id = log[index].attributes[case_id_key]
        num_violations = len(conf_result[index])
        is_fit = num_violations == 0

        diagn_stream.append({"case_id": case_id, "num_violations": num_violations, "is_fit": is_fit})

    return pd.DataFrame(diagn_stream)

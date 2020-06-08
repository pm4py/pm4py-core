from pm4py.util import exec_utils
from enum import Enum
from collections import Counter
from pm4py.objects.dfg.utils import dfg_utils


class Parameters(Enum):
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"


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

    F = open(output_path, "w")
    F.write("%d\n" % (len(activities)))
    for act in activities:
        F.write("%s\n" % (act))

    F.write("%d\n" % (len(start_activities)))
    for act, count in start_activities.items():
        F.write("%dx%d\n" % (activities.index(act), count))

    F.write("%d\n" % (len(end_activities)))
    for act, count in end_activities.items():
        F.write("%dx%d\n" % (activities.index(act), count))

    for el, count in dfg.items():
        F.write("%d>%dx%d\n" % (activities.index(el[0]), activities.index(el[1]), count))

    F.close()

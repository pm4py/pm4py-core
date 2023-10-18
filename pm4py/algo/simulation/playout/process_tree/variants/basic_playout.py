from pm4py.objects.process_tree import semantics
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.process_tree.obj import ProcessTree


class Parameters:
    NO_TRACES = "num_traces"


def apply(tree: ProcessTree, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Generate a log by a playout operation

    Parameters
    ---------------
    tree
        Process tree
    parameters
        Parameters of the algorithm, including:
        - Parameters.NO_TRACES: number of traces of the playout

    Returns
    --------------
    log
        Simulated log
    """
    if parameters is None:
        parameters = {}

    no_traces = exec_utils.get_param_value(Parameters.NO_TRACES, parameters, 1000)

    log = semantics.generate_log(tree, no_traces=no_traces)

    return log

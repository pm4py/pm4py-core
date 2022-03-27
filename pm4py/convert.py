__doc__ = """
Cross-conversions are available between the different event log formats, and the different types of process models
offered in PM4Py.

* Conversion between event log formats
    * `Converting to (XES) event log`_
    * `Converting to Pandas dataframe`_
    * `Converting to event stream`_
* Conversion between process models
    * `Converting to Petri net`_
    * `Converting to BPMN`_
    * `Converting to Process Tree`_
    * `Converting to Reachability Graph`_

.. _Converting to (XES) event log: pm4py.html#pm4py.convert.convert_to_event_log
.. _Converting to Pandas dataframe: pm4py.html#pm4py.convert.convert_to_dataframe
.. _Converting to event stream: pm4py.html#pm4py.convert.convert_to_event_stream
.. _Converting to Petri net: pm4py.html#pm4py.convert.convert_to_petri_net
.. _Converting to BPMN: pm4py.html#pm4py.convert.convert_to_bpmn
.. _Converting to Process Tree: pm4py.html#pm4py.convert.convert_to_process_tree
.. _Converting to Reachability Graph: pm4py.html#pm4py.convert.convert_to_reachability_graph

"""

from typing import Union, Tuple, Optional

import pandas as pd

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.utils import get_properties, __event_log_deprecation_warning
from pm4py.objects.transition_system.obj import TransitionSystem


def convert_to_event_log(obj: Union[pd.DataFrame, EventStream], case_id_key: str = "case:concept:name") -> EventLog:
    """
    Converts a log object to an event log

    Example:

    .. code-block:: python3

       import pandas as pd
       import pm4py

       dataframe = pm4py.read_csv("tests/input_data/running-example.csv")
       dataframe = pm4py.format_dataframe(dataframe, case_id_column='case:concept:name', activity_column='concept:name', timestamp_column='time:timestamp')
       log = pm4py.convert_to_event_log(dataframe)

    Parameters
    -------------
    obj
        Log object
    case_id_key
        attribute to be used as case identifier

    Returns
    -------------
    log
        Event log object
    """
    # Unit test: YES
    if type(obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    from pm4py.objects.conversion.log import converter
    log = converter.apply(obj, variant=converter.Variants.TO_EVENT_LOG, parameters=get_properties(obj, case_id_key=case_id_key))

    __event_log_deprecation_warning(log)

    return log


def convert_to_event_stream(obj: Union[EventLog, pd.DataFrame], case_id_key: str = "case:concept:name") -> EventStream:
    """
    Converts a log object to an event stream

    Example:

    .. code-block:: python3

       import pm4py

       log = pm4py.read_xes("tests/input_data/running-example.xes")
       event_stream = pm4py.convert_to_event_stream(log)

    Parameters
    --------------
    obj
        Log object
    case_id_key
        attribute to be used as case identifier

    Returns
    --------------
    stream
        Event stream object
    """
    # Unit test: YES
    if type(obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    from pm4py.objects.conversion.log import converter
    stream = converter.apply(obj, variant=converter.Variants.TO_EVENT_STREAM, parameters=get_properties(obj, case_id_key=case_id_key))

    __event_log_deprecation_warning(stream)

    return stream


def convert_to_dataframe(obj: Union[EventStream, EventLog]) -> pd.DataFrame:
    """
    Converts a log object to a dataframe

    Example:

    .. code-block:: python3

       import pm4py

       log = pm4py.read_xes("tests/input_data/running-example.xes")
       

    Parameters
    --------------
    obj
        Log object

    Returns
    --------------
    df
        Dataframe
    """
    # Unit test: YES
    if type(obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    from pm4py.objects.conversion.log import converter
    df = converter.apply(obj, variant=converter.Variants.TO_DATA_FRAME, parameters=get_properties(obj))
    return df


def convert_to_bpmn(*args: Union[Tuple[PetriNet, Marking, Marking], ProcessTree]) -> BPMN:
    """
    Converts an object to a BPMN diagram

    Parameters
    --------------
    *args
        Object (process tree)

    Returns
    --------------
    bpmn_diagram
        BPMN diagram
    """
    # Unit test: YES
    from pm4py.objects.process_tree.obj import ProcessTree
    from pm4py.objects.bpmn.obj import BPMN

    if isinstance(args[0], BPMN):
        # the object is already a BPMN
        return args[0]
    elif isinstance(args[0], ProcessTree):
        from pm4py.objects.conversion.process_tree.variants import to_bpmn
        return to_bpmn.apply(args[0])
    else:
        # try to convert the object to a Petri net. Then, use the PM4Py PN-to-BPMN converter
        # to get the BPMN object
        try:
            net, im, fm = convert_to_petri_net(*args)
            from pm4py.objects.conversion.wf_net.variants import to_bpmn
            return to_bpmn.apply(net, im, fm)
        except:
            # don't do nothing and throw the following exception
            pass
    # if no conversion is done, then the format of the arguments is unsupported
    raise Exception("unsupported conversion of the provided object to BPMN")


def convert_to_petri_net(*args: Union[BPMN, ProcessTree, HeuristicsNet, dict]) -> Tuple[PetriNet, Marking, Marking]:
    """
    Converts an object to an (accepting) Petri net

    Parameters
    --------------
    *args
        Object (process tree, BPMN)

    Returns
    --------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    # Unit test: YES
    if isinstance(args[0], PetriNet):
        # the object is already a Petri net
        return args[0], args[1], args[2]
    elif isinstance(args[0], ProcessTree):
        from pm4py.objects.conversion.process_tree.variants import to_petri_net
        return to_petri_net.apply(args[0])
    elif isinstance(args[0], BPMN):
        from pm4py.objects.conversion.bpmn.variants import to_petri_net
        return to_petri_net.apply(args[0])
    elif isinstance(args[0], HeuristicsNet):
        from pm4py.objects.conversion.heuristics_net.variants import to_petri_net
        return to_petri_net.apply(args[0])
    elif isinstance(args[0], dict):
        # DFG
        from pm4py.objects.conversion.dfg.variants import to_petri_net_activity_defines_place
        return to_petri_net_activity_defines_place.apply(args[0], parameters={
            to_petri_net_activity_defines_place.Parameters.START_ACTIVITIES: args[1],
            to_petri_net_activity_defines_place.Parameters.END_ACTIVITIES: args[2]})
    # if no conversion is done, then the format of the arguments is unsupported
    raise Exception("unsupported conversion of the provided object to Petri net")


def convert_to_process_tree(*args: Union[Tuple[PetriNet, Marking, Marking], BPMN]) -> ProcessTree:
    """
    Converts an object to a process tree

    Parameters
    --------------
    *args
        Object (Petri net, BPMN)

    Returns
    --------------
    tree
        Process tree (when the model is block-structured)
    """
    # Unit test: YES
    from pm4py.objects.process_tree.obj import ProcessTree
    from pm4py.objects.petri_net.obj import PetriNet
    if isinstance(args[0], ProcessTree):
        # the object is already a process tree
        return args[0]

    if isinstance(args[0], PetriNet):
        net, im, fm = args[0], args[1], args[2]
    else:
        net, im, fm = convert_to_petri_net(*args)

    from pm4py.objects.conversion.wf_net.variants import to_process_tree
    tree = to_process_tree.apply(net, im, fm)
    if tree is not None:
        return tree

    raise Exception("the object represents a model that cannot be represented as a process tree!")


def convert_to_reachability_graph(*args: Union[Tuple[PetriNet, Marking, Marking], BPMN, ProcessTree]) -> TransitionSystem:
    """
    Converts an object to a reachability graph (transition system)

    Parameters
    --------------
    *args
        Object (Petri net, BPMN)

    Returns
    -------------
    transition_system
        Reachability graph
    """
    # Unit test: YES
    if isinstance(args[0], PetriNet):
        net, im, fm = args[0], args[1], args[2]
    else:
        net, im, fm = convert_to_petri_net(*args)

    from pm4py.objects.petri_net.utils import reachability_graph
    return reachability_graph.construct_reachability_graph(net, im)

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
__doc__ = """
The ``pm4py.convert`` module contains the cross-conversions implemented in ``pm4py``
"""

from typing import Union, Tuple, Optional, Collection

import pandas as pd

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.utils import get_properties, __event_log_deprecation_warning
from pm4py.objects.transition_system.obj import TransitionSystem
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
import networkx as nx


def convert_to_event_log(obj: Union[pd.DataFrame, EventStream], case_id_key: str = "case:concept:name") -> EventLog:
    """
    Converts a DataFrame/EventStream object to an event log object

    :param obj: DataFrame or EventStream object
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``EventLog``
    
    .. code-block:: python3

       import pandas as pd
       import pm4py

       dataframe = pm4py.read_csv("tests/input_data/running-example.csv")
       dataframe = pm4py.format_dataframe(dataframe, case_id_column='case:concept:name', activity_column='concept:name', timestamp_column='time:timestamp')
       log = pm4py.convert_to_event_log(dataframe)
    """
    if type(obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    if check_is_pandas_dataframe(obj):
        check_pandas_dataframe_columns(obj, case_id_key=case_id_key)

    from pm4py.objects.conversion.log import converter
    log = converter.apply(obj, variant=converter.Variants.TO_EVENT_LOG, parameters=get_properties(obj, case_id_key=case_id_key))

    __event_log_deprecation_warning(log)

    return log


def convert_to_event_stream(obj: Union[EventLog, pd.DataFrame], case_id_key: str = "case:concept:name") -> EventStream:
    """
    Converts a log object to an event stream

    :param obj: log object
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``EventStream``
    
    .. code-block:: python3

       import pm4py

       log = pm4py.read_xes("tests/input_data/running-example.xes")
       event_stream = pm4py.convert_to_event_stream(log)

    """
    if type(obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    if check_is_pandas_dataframe(obj):
        check_pandas_dataframe_columns(obj, case_id_key=case_id_key)

    from pm4py.objects.conversion.log import converter
    stream = converter.apply(obj, variant=converter.Variants.TO_EVENT_STREAM, parameters=get_properties(obj, case_id_key=case_id_key))

    __event_log_deprecation_warning(stream)

    return stream


def convert_to_dataframe(obj: Union[EventStream, EventLog]) -> pd.DataFrame:
    """
    Converts a log object to a dataframe

    :param obj: log object
    :rtype: ``pd.DataFrame``
    
    .. code-block:: python3

       import pm4py

       log = pm4py.read_xes("tests/input_data/running-example.xes")
       dataframe = pm4py.convert_to_dataframe(log)
    """
    if type(obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    if check_is_pandas_dataframe(obj):
        check_pandas_dataframe_columns(obj)

    from pm4py.objects.conversion.log import converter
    df = converter.apply(obj, variant=converter.Variants.TO_DATA_FRAME, parameters=get_properties(obj))
    return df


def convert_to_bpmn(*args: Union[Tuple[PetriNet, Marking, Marking], ProcessTree]) -> BPMN:
    """
    Converts an object to a BPMN diagram.
    As an input, either a Petri net (with corresponding initial and final marking) or a process tree can be provided.
    A process tree can always be converted into a BPMN model and thus quality of the result object is guaranteed.
    For Petri nets, the quality of the converison largely depends on the net provided (e.g., sound WF-nets are likely to produce reasonable BPMN models)    

    :param args: petri net (with initial and final marking) or process tree
    :rtype: ``BPMN``
    
    .. code-block:: python3

       import pm4py

       # import a Petri net from a file
       net, im, fm = pm4py.read_pnml("tests/input_data/running-example.pnml")
       bpmn_graph = pm4py.convert_to_bpmn(net, im, fm)
    """
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
    Converts an input model to an (accepting) Petri net.
    The input objects can either be a process tree, BPMN model or a Heuristic net.
    The output is a triple, containing the Petri net and the initial and final markings. The markings are only returned if they can be reasonable derived from the input model.

    :param args: process tree or BPMN
    :rtype: ``Tuple[PetriNet, Marking, Marking]``
    
    .. code-block:: python3

       import pm4py

       # imports a process tree from a PTML file
       process_tree = pm4py.read_ptml("tests/input_data/running-example.ptml")
       net, im, fm = pm4py.convert_to_petri_net(process_tree)
    """
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
    Converts an input model to a process tree.
    The input models can either be Petri nets (marked) or BPMN models.
    For both input types, the conversion is not guaranteed to work, hence, invocation of the method can yield an Exception.

    :param args: petri net (along with initial and final marking) or BPMN
    :rtype: ``ProcessTree``
    
    .. code-block:: python3

       import pm4py

       # imports a BPMN file
       bpmn_graph = pm4py.read_bpmn("tests/input_data/running-example.bpmn")
       # converts the BPMN to a process tree (through intermediate conversion to a Petri net)
       process_tree = pm4py.convert_to_process_tree(bpmn_graph)
    """
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
    Converts an input model to a reachability graph (transition system).
    The input models can either be Petri nets (with markings), BPMN models or process trees.
    The output is the state-space of the model (i.e., the reachability graph), enocdoed as a ``TransitionSystem`` object.

    :param args: petri net (along with initial and final marking), process tree or BPMN
    :rtype: ``TransitionSystem``
    
    .. code-block:: python3

        import pm4py

        # reads a Petri net from a file
        net, im, fm = pm4py.read_pnml("tests/input_data/running-example.pnml")
        # converts it to reachability graph
        reach_graph = pm4py.convert_to_reachability_graph(net, im, fm)
    """
    if isinstance(args[0], PetriNet):
        net, im, fm = args[0], args[1], args[2]
    else:
        net, im, fm = convert_to_petri_net(*args)

    from pm4py.objects.petri_net.utils import reachability_graph
    return reachability_graph.construct_reachability_graph(net, im)


def convert_log_to_ocel(log: Union[EventLog, EventStream, pd.DataFrame], activity_column: str = "concept:name", timestamp_column: str = "time:timestamp", object_types: Collection[str] = ["case:concept:name"], obj_separator: str = " AND ") -> OCEL:
    """
    Converts an event log to an object-centric event log with one or more than one
    object types.

    :param log_obj: log object
    :param activity_column: activity column
    :param timestamp_column: timestamp column
    :param object_types: list of columns to consider as object types
    :param obj_separator: separator between different objects in the same column
    :rtype: ``OCEL``

    .. code-block:: python3
        import pm4py

        ocel = pm4py.convert_log_to_ocel(log, activity_column='concept:name', timestamp_column='time:timestamp',
                        object_types=['case:concept:name'])
    """
    from pm4py.objects.ocel.util import log_ocel
    return log_ocel.log_to_ocel_multiple_obj_types(log, activity_column, timestamp_column, object_types, obj_separator)


def convert_ocel_to_networkx(ocel: OCEL, variant: str = "ocel_to_nx") -> nx.DiGraph:
    """
    Converts an OCEL to a NetworkX DiGraph object.

    :param ocel: object-centric event log
    :param variant: variant of the conversion to use: "ocel_to_nx" -> graph containing event and object IDS and two type of relations (REL=related objects, DF=directly-follows); "ocel_features_to_nx" -> graph containing different types of interconnection at the object level
    :rtype: ``nx.DiGraph``

    .. code-block:: python3
        import pm4py

        nx_digraph = pm4py.convert_ocel_to_networkx(ocel, variant='ocel_to_nx')
    """
    from pm4py.objects.conversion.ocel import converter

    variant1 = None
    if variant == "ocel_to_nx":
        variant1 = converter.Variants.OCEL_TO_NX
    elif variant == "ocel_features_to_nx":
        variant1 = converter.Variants.OCEL_TO_NX

    return converter.apply(ocel, variant=variant1)


def convert_log_to_networkx(log: Union[EventLog, EventStream, pd.DataFrame], include_df: bool = True, case_id_key: str = "concept:name", other_case_attributes_as_nodes: Optional[Collection[str]] = None, event_attributes_as_nodes: Optional[Collection[str]] = None):
    """
    Converts an event log object to a NetworkX DiGraph object.
    The nodes of the graph are the events, the cases (and possibly the attributes of the log).
    The edges are:
    - Connecting each event to the corresponding case (BELONGS_TO type)
    - Connecting every event to the directly-following one (DF type, if enabled)
    - Connecting every case/event to the given attribute values (ATTRIBUTE_EDGE type)

    :param log: log object (EventLog, EventStream, Pandas dataframe)
    :param include_df: include the directly-follows graph relation in the graph (bool)
    :param case_id_attribute: specify which attribute at the case level should be considered the case ID (str)
    :param other_case_attributes_as_nodes: specify which attributes at the case level should be inserted in the graph as nodes (other than the caseID) (list, default empty)
    :param event_attributes_as_nodes: specify which attributes at the event level should be inserted in the graph as nodes (list, default empty)
    :rtype: ``nx.DiGraph``

    .. code-block:: python3
        import pm4py

        nx_digraph = pm4py.convert_log_to_networkx(log, other_case_attributes_as_nodes=['responsible', 'department'], event_attributes_as_nodes=['concept:name', 'org:resource'])
    """
    from pm4py.objects.conversion.log import converter

    return converter.apply(log, variant=converter.Variants.TO_NX, parameters={"include_df": include_df, "case_id_attribute": case_id_key, "other_case_attributes_as_nodes": other_case_attributes_as_nodes, "event_attributes_as_nodes": event_attributes_as_nodes})

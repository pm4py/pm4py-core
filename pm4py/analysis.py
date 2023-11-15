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
"""

from typing import List, Optional, Tuple, Dict, Union, Generator, Set, Any

from pm4py.objects.log.obj import Trace, EventLog, EventStream
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.utils import __event_log_deprecation_warning
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.utils import get_properties, pandas_utils, constants
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns

import pandas as pd
import deprecation


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="this method will be removed in a future release.")
def construct_synchronous_product_net(trace: Trace, petri_net: PetriNet, initial_marking: Marking,
                                      final_marking: Marking) -> Tuple[PetriNet, Marking, Marking]:
    """
    constructs the synchronous product net between a trace and a Petri net process model.

    :param trace: trace of an event log
    :param petri_net: petri net
    :param initial_marking: initial marking
    :param final_marking: final marking

    :rtype: ``Tuple[PetriNet, Marking, Marking]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        log = pm4py.read_xes('log.xes')
        sync_net, sync_im, sync_fm = pm4py.construct_synchronous_product_net(log[0], net, im, fm)
    """
    from pm4py.objects.petri_net.utils.petri_utils import construct_trace_net
    from pm4py.objects.petri_net.utils.synchronous_product import construct
    from pm4py.objects.petri_net.utils.align_utils import SKIP
    trace_net, trace_im, trace_fm = construct_trace_net(trace)
    sync_net, sync_im, sync_fm = construct(trace_net, trace_im, trace_fm, petri_net, initial_marking, final_marking,
                                           SKIP)
    return sync_net, sync_im, sync_fm


def compute_emd(language1: Dict[List[str], float], language2: Dict[List[str], float]) -> float:
    """
    Computes the earth mover distance between two stochastic languages (for example, the first extracted from the log,
    and the second extracted from the process model.

    :param language1: (first) stochastic language
    :param language2: (second) stochastic language
    :rtype: ``float``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes('tests/input_data/running-example.xes')
        language_log = pm4py.get_stochastic_language(log)
        print(language_log)
        net, im, fm = pm4py.read_pnml('tests/input_data/running-example.pnml')
        language_model = pm4py.get_stochastic_language(net, im, fm)
        print(language_model)
        emd_distance = pm4py.compute_emd(language_log, language_model)
        print(emd_distance)
    """
    from pm4py.algo.evaluation.earth_mover_distance import algorithm as earth_mover_distance
    return earth_mover_distance.apply(language1, language2)


def solve_marking_equation(petri_net: PetriNet, initial_marking: Marking,
                           final_marking: Marking, cost_function: Dict[PetriNet.Transition, float] = None) -> float:
    """
    Solves the marking equation of a Petri net.
    The marking equation is solved as an ILP problem.
    An optional transition-based cost function to minimize can be provided as well.

    :param petri_net: petri net
    :param initial_marking: initial marking
    :param final_marking: final marking
    :param cost_function: optional cost function to use when solving the marking equation
    :rtype: ``float``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        heuristic = pm4py.solve_marking_equation(net, im, fm)
    """
    from pm4py.algo.analysis.marking_equation import algorithm as marking_equation

    if cost_function is None:
        cost_function = dict()
        for t in petri_net.transitions:
            cost_function[t] = 1

    me = marking_equation.build(
        petri_net, initial_marking, final_marking, parameters={'costs': cost_function})
    return marking_equation.get_h_value(me)


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="this method will be removed in a future release.")
def solve_extended_marking_equation(trace: Trace, sync_net: PetriNet, sync_im: Marking,
                                    sync_fm: Marking, split_points: Optional[List[int]] = None) -> float:
    """
    Gets an heuristics value (underestimation of the cost of an alignment) between a trace
    and a synchronous product net using the extended marking equation with the standard cost function
    (e.g. sync moves get cost equal to 0, invisible moves get cost equal to 1,
    other move on model / move on log get cost equal to 10000), with an optimal provisioning of the split
    points

    :param trace: trace
    :param sync_net: synchronous product net
    :param sync_im: initial marking (of the sync net)
    :param sync_fm: final marking (of the sync net)
    :param split_points: if specified, the indexes of the events of the trace to be used as split points. If not specified, the split points are identified automatically.
    :rtype: ``float``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        log = pm4py.read_xes('log.xes')
        ext_mark_eq_heu = pm4py.solve_extended_marking_equation(log[0], net, im, fm)
    """
    from pm4py.algo.analysis.extended_marking_equation import algorithm as extended_marking_equation
    parameters = {}
    if split_points is not None:
        parameters[extended_marking_equation.Variants.CLASSIC.value.Parameters.SPLIT_IDX] = split_points
    me = extended_marking_equation.build(
        trace, sync_net, sync_im, sync_fm, parameters=parameters)
    return extended_marking_equation.get_h_value(me)


def check_soundness(petri_net: PetriNet, initial_marking: Marking,
                    final_marking: Marking, print_diagnostics: bool = False) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if a given Petri net is a sound WF-net.
    A Petri net is a WF-net iff:
        - it has a unique source place
        - it has a unique end place
        - every element in the WF-net is on a path from the source to the sink place
    A WF-net is sound iff:
        - it contains no live-locks
        - it contains no deadlocks
        - we are able to always reach the final marking
    For a formal definition of sound WF-net, consider: http://www.padsweb.rwth-aachen.de/wvdaalst/publications/p628.pdf
    In the returned object, the first element is a boolean indicating if the Petri net is a sound workflow net.
    The second element is a set of diagnostics collected while running WOFLAN
    (expressed as a dictionary associating the keys [name of the diagnostics] with the corresponding diagnostics).

    :param petri_net: petri net
    :param initial_marking: initial marking
    :param final_marking: final marking
    :param print_diagnostics: boolean value that sets up additional prints during the execution of WOFLAN
    :rtype: ``Tuple[bool, Dict[str, Any]]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        is_sound = pm4py.check_soundness(net, im, fm)
    """
    from pm4py.algo.analysis.woflan import algorithm as woflan
    return woflan.apply(petri_net, initial_marking, final_marking,
                        parameters={"return_asap_when_not_sound": True, "return_diagnostics": True, "print_diagnostics": print_diagnostics})


def cluster_log(log: Union[EventLog, EventStream, pd.DataFrame], sklearn_clusterer=None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Generator[EventLog, None, None]:
    """
    Apply clustering to the provided event log
    (method based on the extraction of profiles for the traces of the event log)
    based on a Scikit-Learn clusterer (default: K-means with two clusters)

    :param log: log object
    :param sklearn_clusterer: the Scikit-Learn clusterer to be used (default: KMeans(n_clusters=2, random_state=0, n_init="auto"))
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Generator[pd.DataFrame, None, None]``

    .. code-block:: python3

        import pm4py

        for clust_log in pm4py.cluster_log(df):
            print(clust_log)
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)
    if sklearn_clusterer is not None:
        properties["sklearn_clusterer"] = sklearn_clusterer

    from pm4py.algo.clustering.profiles import algorithm as clusterer
    return clusterer.apply(log, parameters=properties)


def insert_artificial_start_end(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name", artificial_start=constants.DEFAULT_ARTIFICIAL_START_ACTIVITY, artificial_end=constants.DEFAULT_ARTIFICIAL_END_ACTIVITY) -> Union[EventLog, pd.DataFrame]:
    """
    Inserts the artificial start/end activities in an event log / Pandas dataframe

    :param log: event log / Pandas dataframe
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :param artificial_start: the symbol to be used as artificial start activity
    :param artificial_end: the symbol to be used as artificial end activity
    :rtype: ``Union[EventLog, pd.DataFrame]``

    .. code-block:: python3

        import pm4py

        dataframe = pm4py.insert_artificial_start_end(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)
    properties[constants.PARAM_ARTIFICIAL_START_ACTIVITY] = artificial_start
    properties[constants.PARAM_ARTIFICIAL_END_ACTIVITY] = artificial_end

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)
        from pm4py.objects.log.util import dataframe_utils
        return dataframe_utils.insert_artificial_start_end(log, parameters=properties)
    else:
        from pm4py.objects.log.util import artificial
        return artificial.insert_artificial_start_end(log, parameters=properties)


def insert_case_service_waiting_time(log: Union[EventLog, pd.DataFrame], service_time_column: str = "@@service_time",
                                     sojourn_time_column: str = "@@sojourn_time",
                                     waiting_time_column: str = "@@waiting_time", activity_key: str = "concept:name",
                                     timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name",
                                     start_timestamp_key: str = "time:timestamp") -> pd.DataFrame:
    """
    Inserts the service/waiting/sojourn times of the case in the dataframe.

    :param log: event log / Pandas dataframe
    :param service_time_column: column to be used for the service time
    :param sojourn_time_column: column to be used for the sojourn time
    :param waiting_time_column: column to be used for the waiting time
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :param start_timestamp_key: attribute to be used as start timestamp
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        dataframe = pm4py.insert_case_service_waiting_time(dataframe, activity_key='concept:name', timestamp_key='time:timestamp', case_id_key='case:concept:name', start_timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)

    log = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME, parameters=properties)

    return pandas_utils.insert_case_service_waiting_time(log, case_id_column=case_id_key, timestamp_column=timestamp_key, start_timestamp_column=start_timestamp_key, service_time_column=service_time_column, waiting_time_column=waiting_time_column, sojourn_time_column=sojourn_time_column)


def insert_case_arrival_finish_rate(log: Union[EventLog, pd.DataFrame], arrival_rate_column="@@arrival_rate", finish_rate_column="@@finish_rate",
                                    activity_key: str = "concept:name",
                                     timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name",
                                     start_timestamp_key: str = "time:timestamp") -> pd.DataFrame:
    """
    Inserts the arrival/finish rates of the case in the dataframe.
    The arrival rate is computed as the difference between the start time of the case and the start time of the previous case to start.
    The finish rate is computed as the difference between the end time of the case and the end time of the next case to end.

    :param log: event log / Pandas dataframe
    :param arrival_rate_column: column to be used for the arrival rate
    :param finish_rate_column: column to be used for the finish rate
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :param start_timestamp_key: attribute to be used as start timestamp
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        dataframe = pm4py.insert_case_arrival_finish_rate(dataframe, activity_key='concept:name', timestamp_key='time:timestamp', case_id_key='case:concept:name', start_timestamp_key='time:timestamp')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)

    log = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME, parameters=properties)

    return pandas_utils.insert_case_arrival_finish_rate(log, case_id_column=case_id_key, timestamp_column=timestamp_key, start_timestamp_column=start_timestamp_key, arrival_rate_column=arrival_rate_column, finish_rate_column=finish_rate_column)


def check_is_workflow_net(net: PetriNet) -> bool:
    """
    Checks if the input Petri net satisfies the WF-net conditions:
    1. unique source place
    2. unique sink place
    3. every node is on a path from the source to the sink

    :param net: petri net
    :rtype: ``bool``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        is_wfnet = pm4py.check_is_workflow_net(net, im, fm)
    """
    from pm4py.algo.analysis.workflow_net import algorithm
    return algorithm.apply(net)


def maximal_decomposition(net: PetriNet, im: Marking, fm: Marking) -> List[Tuple[PetriNet, Marking, Marking]]:
    """
    Calculate the maximal decomposition of an accepting Petri net.

    :param net: petri net
    :param im: initial marking
    :param fm: final marking
    :rtype: ``List[Tuple[PetriNet, Marking, Marking]]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        list_nets = pm4py.maximal_decomposition(net, im, fm)
        for anet in list_nets:
            subnet, subim, subfm = anet
            pm4py.view_petri_net(subnet, subim, subfm, format='svg')
    """
    from pm4py.objects.petri_net.utils.decomposition import decompose
    return decompose(net, im, fm)


def generate_marking(net: PetriNet, place_or_dct_places: Union[str, PetriNet.Place, Dict[str, int], Dict[PetriNet.Place, int]]) -> Marking:
    """
    Generate a marking for a given Petri net

    :param net: petri net
    :param place_or_dct_places: place, or dictionary of places, to be used in the marking. Possible values: single Place object for the marking; name of the place for the marking; dictionary associating to each place its number of tokens; dictionary associating to names of places a number of tokens.
    :rtype: ``Marking``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        marking = pm4py.generate_marking(net, {'source': 2})
    """
    dct_places = {x.name: x for x in net.places}
    if isinstance(place_or_dct_places, PetriNet.Place):
        # we specified a single Place object for the marking
        return Marking({place_or_dct_places: 1})
    elif isinstance(place_or_dct_places, str):
        # we specified the name of a place for the marking
        return Marking({dct_places[place_or_dct_places]: 1})
    elif isinstance(place_or_dct_places, dict):
        dct_keys = list(place_or_dct_places)
        if dct_keys:
            if isinstance(dct_keys[0], PetriNet.Place):
                # we specified a dictionary associating to each place its number of tokens
                return Marking(place_or_dct_places)
            elif isinstance(dct_keys[0], str):
                # we specified a dictionary associating to names of places a number of tokens
                return Marking({dct_places[x]: y for x, y in place_or_dct_places.items()})


def reduce_petri_net_invisibles(net: PetriNet) -> PetriNet:
    """
    Reduce the number of invisibles transitions in the provided Petri net.

    :param net: petri net
    :rtype: ``PetriNet``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        net = pm4py.reduce_petri_net_invisibles(net)
    """
    from pm4py.objects.petri_net.utils import reduction
    return reduction.apply_simple_reduction(net)


def reduce_petri_net_implicit_places(net: PetriNet, im: Marking, fm: Marking) -> Tuple[PetriNet, Marking, Marking]:
    """
    Reduce the number of invisibles transitions in the provided Petri net.

    :param net: petri net
    :param im: initial marking
    :param fm: final marking
    :rtype: ``Tuple[PetriNet, Marking, Marking]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        net = pm4py.reduce_petri_net_implicit_places(net, im, fm)
    """
    from pm4py.objects.petri_net.utils import murata
    return murata.apply_reduction(net, im, fm)


def get_enabled_transitions(net: PetriNet, marking: Marking) -> Set[PetriNet.Transition]:
    """
    Gets the transitions enabled in a given marking

    :param net: Petri net
    :param marking: marking
    :rtype: ``Set[PetriNet.Transition]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('tests/input_data/running-example.pnml')
        # gets the transitions enabled in the initial marking
        enabled_transitions = pm4py.get_enabled_transitions(net, im)
    """
    from pm4py.objects.petri_net import semantics
    return semantics.enabled_transitions(net, marking)

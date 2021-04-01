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
from typing import Dict, Union, List, Tuple
from typing import Set

import pandas as pd

from pm4py.objects.log.obj import EventLog, Trace
from pm4py.util.pandas_utils import check_is_dataframe, check_dataframe_columns


def get_start_activities(log: Union[EventLog, pd.DataFrame]) -> Dict[str, int]:
    """
    Returns the start activities from a log object

    Parameters
    ---------------
    log
        Log object

    Returns
    ---------------
    start_activities
        Dictionary of start activities along with their count
    """
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.statistics.start_activities.pandas import get
        return get.get_start_activities(log)
    else:
        from pm4py.statistics.start_activities.log import get
        return get.get_start_activities(log)


def get_end_activities(log: Union[EventLog, pd.DataFrame]) -> Dict[str, int]:
    """
    Returns the end activities of a log

    Parameters
    ---------------
    log
        Lob object

    Returns
    ---------------
    end_activities
        Dictionary of end activities along with their count
    """
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.statistics.end_activities.pandas import get
        return get.get_end_activities(log)
    else:
        from pm4py.statistics.end_activities.log import get
        return get.get_end_activities(log)


def get_attributes(log: Union[EventLog, pd.DataFrame]) -> List[str]:
    """
    Returns the attributes at the event level of the log

    Parameters
    ---------------
    log
        Log object

    Returns
    ---------------
    attributes_list
        List of attributes contained in the log
    """
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        return list(log.columns)
    else:
        from pm4py.statistics.attributes.log import get
        return list(get.get_all_event_attributes_from_log(log))


def get_trace_attributes(log: Union[EventLog, pd.DataFrame]) -> List[str]:
    """
    Gets the attributes at the trace level of a log object

    Parameters
    ----------------
    log
        Log object

    Returns
    ---------------
    trace_attributes_list
        List of attributes at the trace level
    """
    from pm4py.util import constants
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        return [x for x in list(log.columns) if x.startswith(constants.CASE_ATTRIBUTE_PREFIX)]
    else:
        from pm4py.statistics.attributes.log import get
        return list(get.get_all_trace_attributes_from_log(log))


def get_attribute_values(log: Union[EventLog, pd.DataFrame], attribute: str) -> Dict[str, int]:
    """
    Returns the values for a specified attribute

    Parameters
    ---------------
    log
        Log object
    attribute
        Attribute

    Returns
    ---------------
    attribute_values
        Dictionary of values along with their count
    """
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.statistics.attributes.pandas import get
        return get.get_attribute_values(log, attribute)
    else:
        from pm4py.statistics.attributes.log import get
        return get.get_attribute_values(log, attribute)


def get_trace_attribute_values(log: Union[EventLog, pd.DataFrame], attribute: str) -> Dict[str, int]:
    """
    Returns the values for a specified trace attribute

    Parameters
    ---------------
    log
        Log object
    attribute
        Attribute

    Returns
    ---------------
    attribute_values
        Dictionary of values along with their count
    """
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.statistics.attributes.pandas import get
        return get.get_attribute_values(log, attribute)
    else:
        from pm4py.statistics.attributes.log import get
        return get.get_trace_attribute_values(log, attribute)


def get_variants(log: Union[EventLog, pd.DataFrame]) -> Dict[str, List[Trace]]:
    """
    Gets the variants from the log

    Parameters
    --------------
    log
        Event log

    Returns
    --------------
    variants
        Dictionary of variants along with their count
    """
    import pm4py
    if pm4py.util.variants_util.VARIANT_SPECIFICATION == pm4py.util.variants_util.VariantsSpecifications.STRING:
        import warnings
        warnings.warn('pm4py.get_variants is deprecated. Please use pm4py.get_variants_as_tuples instead.')
    if pm4py.util.variants_util.VARIANT_SPECIFICATION == pm4py.util.variants_util.VariantsSpecifications.LIST:
        raise Exception('Please use pm4py.get_variants_as_tuples')
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.statistics.variants.pandas import get
        return get.get_variants_count(log)
    else:
        from pm4py.statistics.variants.log import get
        return get.get_variants(log)


def get_variants_as_tuples(log: Union[EventLog, pd.DataFrame]) -> Dict[Tuple[str], List[Trace]]:
    """
    Gets the variants from the log
    (where the keys are tuples and not strings)

    Parameters
    --------------
    log
        Event log

    Returns
    --------------
    variants
        Dictionary of variants along with their count
    """
    import pm4py
    # the behavior of PM4Py is changed to allow this to work
    pm4py.util.variants_util.VARIANT_SPECIFICATION = pm4py.util.variants_util.VariantsSpecifications.LIST
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.statistics.variants.pandas import get
        return get.get_variants_count(log)
    else:
        from pm4py.statistics.variants.log import get
        return get.get_variants(log)


def get_minimum_self_distances(log: EventLog) -> Dict[str, int]:
    '''
    This algorithm computes the minimum self-distance for each activity observed in an event log.
    The self distance of a in <a> is infinity, of a in <a,a> is 0, in <a,b,a> is 1, etc.
    The minimum self distance is the minimal observed self distance value in the event log.

    Parameters
    ----------
    log
        event log (either pandas.DataFrame, EventLog or EventStream)

    Returns
    -------
        dict mapping an activity to its self-distance, if it exists, otherwise it is not part of the dict.
    '''
    from pm4py.algo.discovery.minimum_self_distance import algorithm as msd_algo
    return msd_algo.apply(log)


def get_minimum_self_distance_witnesses(log: EventLog) -> Dict[str, Set[str]]:
    '''
        This function derives the minimum self distance witnesses.
        The self distance of a in <a> is infinity, of a in <a,a> is 0, in <a,b,a> is 1, etc.
        The minimum self distance is the minimal observed self distance value in the event log.
        A 'witness' is an activity that witnesses the minimum self distance.
        For example, if the minimum self distance of activity a in some log L is 2, then,
        if trace <a,b,c,a> is in log L, b and c are a witness of a.

        Parameters
        ----------
        log
            Event Log to use

        Returns
        -------
        Dictionary mapping each activity to a set of witnesses.

        '''
    from pm4py.algo.discovery.minimum_self_distance import algorithm as msd_algo
    from pm4py.algo.discovery.minimum_self_distance import utils as msdw_algo
    return msdw_algo.derive_msd_witnesses(log, msd_algo.apply(log))


def get_case_arrival_average(log: Union[EventLog, pd.DataFrame]) -> float:
    """
    Gets the average difference between the start times of two consecutive cases

    Parameters
    ---------------
    log
        Log object

    Returns
    ---------------
    case_arrival_average
        Average difference between the start times of two consecutive cases
    """
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.statistics.traces.pandas import case_arrival
        return case_arrival.get_case_arrival_avg(log)
    else:
        from pm4py.statistics.traces.log import case_arrival
        return case_arrival.get_case_arrival_avg(log)

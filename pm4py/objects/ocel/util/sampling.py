from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel import constants
import random
from pm4py.objects.ocel.util import filtering_utils
from copy import copy
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


class Parameters(Enum):
    OBJECT_ID = constants.PARAM_OBJECT_ID
    EVENT_ID = constants.PARAM_EVENT_ID
    NUM_ENTITIES = "num_entities"


def sample_ocel_events(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Keeps a sample of the events of an object-centric event log

    Parameters
    ------------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
            - Parameters.EVENT_ID => event identifier
            - Parameters.NUM_ENTITIES => number of events

    Returns
    ------------------
    sampled_ocel
        Sampled object-centric event log
    """
    if parameters is None:
        parameters = {}

    event_id_column = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    num_entities = exec_utils.get_param_value(Parameters.NUM_ENTITIES, parameters, 100)

    events = list(ocel.events[event_id_column].unique())
    num_events = min(len(events), num_entities)

    random.shuffle(events)
    picked_events = events[:num_events]

    ocel = copy(ocel)
    ocel.events = ocel.events[ocel.events[event_id_column].isin(picked_events)]

    return filtering_utils.propagate_event_filtering(ocel, parameters=parameters)


def sample_ocel_objects(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Random samples the objects of the object-centric event log.
    Then, only the events related to at least one of these objects are filtered from the event log.
    As a note, the relationships between the different objects are probably going to be ruined by
    this sampling.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
            - Parameters.OBJECT_ID => object identifier
            - Parameters.NUM_ENTITIES => number of objects to retain

    Returns
    ----------------
    sampled_ocel
        Sampled object-centric event log
    """
    if parameters is None:
        parameters = {}

    object_id_column = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel.object_id_column)
    num_entities = exec_utils.get_param_value(Parameters.NUM_ENTITIES, parameters, 100)

    objects = list(ocel.objects[object_id_column].unique())
    num_objects = min(len(objects), num_entities)

    random.shuffle(objects)
    picked_objects = objects[:num_objects]

    ocel = copy(ocel)
    ocel.objects = ocel.objects[ocel.objects[object_id_column].isin(picked_objects)]

    return filtering_utils.propagate_object_filtering(ocel, parameters=parameters)

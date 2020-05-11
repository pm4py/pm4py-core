from enum import Enum
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY


class Parameters(Enum):
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    FORMAT = "format"
    MAX_NO_EDGES_IN_DIAGRAM = "maxNoOfEdgesInDiagram"
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"

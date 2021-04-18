from enum import Enum

import warnings

warnings.warn("pm4py.statistics.attributes.parameters is deprecated. please use the variant-specific parameters.")


class Parameters(Enum):
    GRAPH_POINTS = "graph_points"
    POINT_TO_SAMPLE = "points_to_sample"

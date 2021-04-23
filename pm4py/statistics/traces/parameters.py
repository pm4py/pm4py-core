from enum import Enum

import warnings

warnings.warn("pm4py.visualization.traces.parameters is deprecated. please use the variant-specific parameters instead.")


class Parameters(Enum):
    GRAPH_POINTS = "graph_points"
    POINT_TO_SAMPLE = "points_to_sample"

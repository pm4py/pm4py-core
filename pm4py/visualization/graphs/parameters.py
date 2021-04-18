from enum import Enum
import warnings


warnings.warn(
    "pm4py.visualization.graphs.parameters is deprecated. please use the parameters inside the visualization variant.")


class Parameters(Enum):
    TITLE = "title"
    FORMAT = "format"

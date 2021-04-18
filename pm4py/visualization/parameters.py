from enum import Enum
import warnings

warnings.warn(
    "pm4py.visualization.parameters is deprecated. please use the parameters inside the visualization variant.")


class Parameters(Enum):
    FORMAT = "format"

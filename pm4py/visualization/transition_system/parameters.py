import warnings
from enum import Enum

warnings.warn(
    "pm4py.visualization.transition_system.parameters is deprecated. please use the parameters inside the visualization variant.")


class Parameters(Enum):
    FORMAT = "format"
    SHOW_LABELS = "show_labels"
    SHOW_NAMES = "show_names"
    FORCE_NAMES = "force_names"
    FILLCOLORS = "fillcolors"
    FONT_SIZE = "font_size"

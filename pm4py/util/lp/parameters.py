from enum import Enum
import warnings


warnings.warn("pm4py.util.lp.parameters is deprecated. please use the parameters inside the single variants.")


class Parameters(Enum):
    REQUIRE_ILP = "require_ilp"

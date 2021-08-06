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
from pm4py.algo.evaluation.simplicity.variants import arc_degree
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
import pandas as pd


class Variants(Enum):
    SIMPLICITY_ARC_DEGREE = arc_degree


SIMPLICITY_ARC_DEGREE = Variants.SIMPLICITY_ARC_DEGREE

VERSIONS = {SIMPLICITY_ARC_DEGREE}


def apply(petri_net: PetriNet, parameters: Optional[Dict[Any, Any]] = None, variant=SIMPLICITY_ARC_DEGREE) -> float:
    return exec_utils.get_variant(variant).apply(petri_net, parameters=parameters)

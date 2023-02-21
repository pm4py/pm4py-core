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
from pm4py.algo.discovery.ocel.link_analysis.variants import classic
from enum import Enum
from pm4py.util import exec_utils
import pandas as pd
from typing import Optional, Dict, Any
from pm4py.objects.log.obj import EventLog, EventStream
from typing import Union
from pm4py.objects.conversion.log import converter


class Variants(Enum):
    CLASSIC = classic


def apply(log: Union[EventLog, EventStream, pd.DataFrame], variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Applies a link analysis algorithm on the provided log object.

    Parameters
    -----------------
    log
        Event log
    variant
        Variant of the algorithm to consider
    parameters
        Variant-specific parameters

    Returns
    -----------------
    link_analysis_dataframe
        Link analysis dataframe
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(converter.apply(log, variant=converter.Variants.TO_DATA_FRAME, parameters=parameters), parameters=parameters)

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
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from enum import Enum
from pm4py.util import exec_utils
from pm4py.algo.label_splitting.variants import contextual


class Variants(Enum):
    CONTEXTUAL = contextual


def apply(log: Union[EventLog, EventStream, pd.DataFrame], variant=Variants.CONTEXTUAL, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Applies a technique of label-splitting, to distinguish between different meanings of the same
    activity. The result is a Pandas dataframe where the label-splitting has been applied.

    Minimum Viable Example:

        import pm4py
        from pm4py.algo.label_splitting import algorithm as label_splitter

        log = pm4py.read_xes("tests/input_data/receipt.xes")
        log2 = label_splitter.apply(log)


    Parameters
    ---------------
    log
        Event log
    parameters
        Variant-specific parameters

    Returns
    ---------------
    dataframe
        Pandas dataframe with the re-labeling
    """
    return exec_utils.get_variant(variant).apply(log, parameters)

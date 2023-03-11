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
from enum import Enum
from pm4py.util import exec_utils
from pm4py.algo.clustering.profiles.variants import sklearn_profiles
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Optional, Dict, Any, Generator, Union


class Variants(Enum):
    SKLEARN_PROFILES = sklearn_profiles


def apply(log: Union[EventLog, EventStream, pd.DataFrame], variant=Variants.SKLEARN_PROFILES, parameters: Optional[Dict[Any, Any]] = None) -> Generator[EventLog, None, None]:
    """
    Apply clustering to the provided event log
    (methods based on the extraction of profiles for the traces of the event log)

    Implements the approach described in:
    Song, Minseok, Christian W. Günther, and Wil MP Van der Aalst. "Trace clustering in process mining." Business Process Management Workshops: BPM 2008 International Workshops, Milano, Italy, September 1-4, 2008. Revised Papers 6. Springer Berlin Heidelberg, 2009.

    Parameters
    ----------------
    log
        Event log
    variant
        Variant of the clustering to be used, available values:
        - Variants.SKLEARN_PROFILES
    parameters
        Variant-specific parameters

    Returns
    ----------------
    generator
        Generator of dataframes (clusters)
    """
    return exec_utils.get_variant(variant).apply(log, parameters=parameters)

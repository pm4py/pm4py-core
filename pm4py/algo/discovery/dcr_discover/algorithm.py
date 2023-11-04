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
from copy import deepcopy

from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils
from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
from pm4py.algo.discovery.dcr_discover.extenstions import roles
from enum import Enum
import pandas as pd
from typing import Union, Any, Optional, Dict, Tuple


class Variants(Enum):
    DCR_BASIC = dcr_discover
    DCR_ROLES = roles
    # DCR_SUBPROCESS = subprocess


DCR_BASIC = Variants.DCR_BASIC
DCR_ROLES = Variants.DCR_ROLES
VERSIONS = {DCR_BASIC, DCR_ROLES}


# DCR_SUBPROCESS = Variants.DCR_SUBPROCESS
# VERSIONS = {DCR_BASIC, DCR_ROLES, DCR_SUBPROCESS}


def apply(log: Union[EventLog, pd.DataFrame], variant=DCR_BASIC, findAdditionalConditions: bool = True,
          post_process=None, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[Any, dict]:
    """
    discover a DCR graph from a provided event log, implemented the DisCoveR algorithm presented in [1]_.
    Allows for mining for additional attribute currently implemented mining of organisational attributes.

    Parameters
    ---------------
    log
        log object (EventLog, pandas dataframe)
    variant
        Variant of the algorithm to use:
        - DCR_BASIC
    findAdditionalConditions:
        Parameter determining if the miner should include an extra step of mining for extra conditions
        - [True, False]

    post_process
        kind of post process mining to handle further patterns
        - DCR_ROLES

    parameters
        variant specific parameters
        findAdditionalConditions: [True or False]
    Returns
    ---------------
    dcr graph
        DCR graph (as an object) containing eventId, set of activities, mapping of event to activities,
            condition relations, response relation, include relations and exclude relations.
        possible to return variant of different dcr graph depending on which variant, basic, roles, etc.

    References
    ----------
    .. [1]
        C. O. Back et al. "DisCoveR: accurate and efficient discovery of declarative process models",
        International Journal on Software Tools for Technology Transfer, 2022, 24:563–587. 'DOI' <https://doi.org/10.1007/s10009-021-00616-0>_.

    """

    input_log = deepcopy(log)
    G, la = exec_utils.get_variant(variant).apply(input_log, findAdditionalConditions=findAdditionalConditions,
                                                  parameters=parameters)
    if post_process is None:
        post_process = set()
    if 'roles' in post_process:
        G = exec_utils.get_variant(DCR_ROLES).apply(input_log, G, parameters=parameters)

    return G, la
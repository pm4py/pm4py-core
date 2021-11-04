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
from typing import Optional, Dict, Any

from pm4py.streaming.algo.conformance.temporal.variants import classic
from pm4py.util import exec_utils
from pm4py.util import typing


class Variants(Enum):
    CLASSIC = classic


def apply(temporal_profile: typing.TemporalProfile, variant=Variants.CLASSIC,
          parameters: Optional[Dict[Any, Any]] = None):
    """
    Initialize the streaming conformance checking

    Parameters
    ---------------
    temporal_profile
        Temporal profile
    variant
        Variant of the algorithm, possible values:
        - Variants.CLASSIC
    parameters
        Parameters of the algorithm, including:
         - Parameters.ACTIVITY_KEY => the attribute to use as activity
         - Parameters.START_TIMESTAMP_KEY => the attribute to use as start timestamp
         - Parameters.TIMESTAMP_KEY => the attribute to use as timestamp
         - Parameters.ZETA => multiplier for the standard deviation
         - Parameters.CASE_ID_KEY => column to use as case identifier
         - Parameters.DICT_VARIANT => the variant of dictionary to use
         - Parameters.CASE_DICT_ID => the identifier of the case dictionary
         - Parameters.DEV_DICT_ID => the identifier of the deviations dictionary
    """
    return exec_utils.get_variant(variant).apply(temporal_profile, parameters=parameters)

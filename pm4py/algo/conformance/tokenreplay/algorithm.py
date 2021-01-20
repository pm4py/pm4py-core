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
from pm4py.algo.conformance.tokenreplay.variants import token_replay, backwards
from pm4py.objects.conversion.log import converter as log_converter
from enum import Enum
from pm4py.util import exec_utils

class Variants(Enum):
    TOKEN_REPLAY = token_replay
    BACKWARDS = backwards

VERSIONS = {Variants.TOKEN_REPLAY, Variants.BACKWARDS}
DEFAULT_VARIANT = Variants.TOKEN_REPLAY


def apply(log, net, initial_marking, final_marking, parameters=None, variant=DEFAULT_VARIANT):
    """
    Method to apply token-based replay
    
    Parameters
    -----------
    log
        Log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Activity key
    variant
        Variant of the algorithm to use:
            - Variants.TOKEN_REPLAY
            - Variants.BACKWARDS
    """
    if parameters is None:
        parameters = {}
    return exec_utils.get_variant(variant).apply(log_converter.apply(log, parameters, log_converter.TO_EVENT_LOG), net, initial_marking,
                             final_marking, parameters=parameters)


def get_diagnostics_dataframe(log, tbr_output, variant=DEFAULT_VARIANT, parameters=None):
    """
    Gets the results of token-based replay in a dataframe

    Parameters
    --------------
    log
        Event log
    tbr_output
        Output of the token-based replay technique
    variant
        Variant of the algorithm to use:
            - Variants.TOKEN_REPLAY
            - Variants.BACKWARDS

    Returns
    --------------
    dataframe
        Diagnostics dataframe
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).get_diagnostics_dataframe(log, tbr_output, parameters=parameters)

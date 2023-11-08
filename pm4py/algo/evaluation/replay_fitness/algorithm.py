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
from pm4py.algo.evaluation.replay_fitness.variants import alignment_based, token_replay
from pm4py.algo.conformance import alignments
from pm4py.util import exec_utils
from pm4py.objects.petri_net.utils.check_soundness import check_easy_soundness_net_in_fin_marking
from enum import Enum
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
import pandas as pd


class Variants(Enum):
    ALIGNMENT_BASED = alignment_based
    TOKEN_BASED = token_replay


class Parameters(Enum):
    ALIGN_VARIANT = "align_variant"


ALIGNMENT_BASED = Variants.ALIGNMENT_BASED
TOKEN_BASED = Variants.TOKEN_BASED

VERSIONS = {ALIGNMENT_BASED, TOKEN_BASED}


def apply(log: Union[EventLog, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, parameters: Optional[Dict[Union[str, Parameters], Any]] = None, variant=None, align_variant=None) -> Dict[str, Any]:
    """
    Apply fitness evaluation starting from an event log and a marked Petri net,
    by using one of the replay techniques provided by PM4Py

    Parameters
    -----------
    log
        Trace log object
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters related to the replay algorithm
    variant
        Chosen variant:
            - Variants.ALIGNMENT_BASED
            - Variants.TOKEN_BASED
    align_variant
        Alignments variant (for alignment-based replay)

    Returns
    ----------
    fitness_eval
        Fitness evaluation
    """
    if parameters is None:
        parameters = {}

    # execute the following part of code when the variant is not specified by the user
    if variant is None:
        if not (
                check_easy_soundness_net_in_fin_marking(petri_net, initial_marking,
                                                                              final_marking)):
            # in the case the net is not a easy sound workflow net, we must apply token-based replay
            variant = TOKEN_BASED
        else:
            # otherwise, use the align-etconformance approach (safer, in the case the model contains duplicates)
            variant = ALIGNMENT_BASED

    if variant == TOKEN_BASED:
        # execute the token-based replay variant
        return exec_utils.get_variant(variant).apply(log,
                                                     petri_net,
                                                     initial_marking, final_marking, parameters=parameters)
    else:
        # execute the alignments based variant, with the specification of the alignments variant
        if align_variant is None:
            align_variant = alignments.petri_net.algorithm.DEFAULT_VARIANT
        return exec_utils.get_variant(variant).apply(log,
                                                     petri_net,
                                                     initial_marking, final_marking, align_variant=align_variant,
                                                     parameters=parameters)


def evaluate(results, parameters=None, variant=TOKEN_BASED):
    """
    Evaluate replay results when the replay algorithm has already been applied

    Parameters
    -----------
    results
        Results of the replay algorithm
    parameters
        Possible parameters passed to the evaluation
    variant
        Indicates which evaluator is called

    Returns
    -----------
    fitness_eval
        Fitness evaluation
    """
    return exec_utils.get_variant(variant).evaluate(results, parameters=parameters)

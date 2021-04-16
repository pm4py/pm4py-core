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
from pm4py.simulation.playout.variants import basic_playout, extensive, stochastic_playout
from pm4py.util import exec_utils
from enum import Enum
import deprecation
from pm4py.meta import VERSION
import warnings


class Variants(Enum):
    BASIC_PLAYOUT = basic_playout
    STOCHASTIC_PLAYOUT = stochastic_playout
    EXTENSIVE = extensive


DEFAULT_VARIANT = Variants.BASIC_PLAYOUT
VERSIONS = {Variants.BASIC_PLAYOUT, Variants.EXTENSIVE, Variants.STOCHASTIC_PLAYOUT}


@deprecation.deprecated(deprecated_in="2.2.5", removed_in="3.0",
                        current_version=VERSION,
                        details="Use the pm4py.algo.simulation.playout package")
def apply(net, initial_marking, final_marking=None, parameters=None, variant=DEFAULT_VARIANT):
    """
    Do the playout of a Petrinet generating a log

    Parameters
    -----------
    net
        Petri net to play-out
    initial_marking
        Initial marking of the Petri net
    final_marking
        (if provided) Final marking of the Petri net
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm to use:
            - Variants.BASIC_PLAYOUT: selects random traces from the model, without looking at the
            frequency of the transitions
            - Variants.STOCHASTIC_PLAYOUT: selects random traces from the model, looking at the
            stochastic frequency of the transitions. Requires the provision of the stochastic map
            or the log.
            - Variants.EXTENSIVE: gets all the traces from the model. can be expensive
    """
    warnings.warn("Use the pm4py.algo.simulation.playout package")
    return exec_utils.get_variant(variant).apply(net, initial_marking, final_marking=final_marking,
                                                 parameters=parameters)

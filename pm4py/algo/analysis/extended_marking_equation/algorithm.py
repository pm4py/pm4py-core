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

from pm4py.algo.analysis.extended_marking_equation.variants import classic
from pm4py.objects.log.obj import Trace
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


def build(trace: Trace, sync_net: PetriNet, sync_im: Marking, sync_fm: Marking, variant=Variants.CLASSIC,
          parameters: Optional[Dict[Any, Any]] = None) -> Any:
    """
    Builds the extended marking equation out of a trace and a synchronous product net

    Parameters
    ---------------
    trace
        Trace
    sync_net
        Synchronous product net
    sync_im
        Initial marking (of sync net)
    sync_fm
        Final marking (of sync net)
    variant
        Variant of the algorithm to use, possible values:
        - Variants.CLASSIC
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY => attribute to use as case identifier
        - Parameters.ACTIVITY_KEY => attribute to use as activity
        - Parameters.COSTS => (if provided) the cost function (otherwise the default cost function is applied)
        - Parameters.SPLIT_IDX => (if provided) the split points as indices of elements of the trace
            (e.g. for ["A", "B", "C", "D", "E"], specifying [1,3] as split points means splitting at "B" and "D").
            If not provided, some split points at uniform distances are found.
        - Parameters.MAX_K_VALUE => the maximum number of split points that is allowed (trim the specified indexes
            if necessary).
        - Parameters.INCIDENCE_MATRIX => (if provided) the incidence matrix associated to the sync product net
        - Parameters.A => (if provided) the A numpy matrix of the incidence matrix
        - Parameters.CONSUMPTION_MATRIX => (if provided) the consumption matrix associated to the sync product net
        - Parameters.C => (if provided) the C numpy matrix of the consumption matrix
        - Parameters.FULL_BOOTSTRAP_REQUIRED => The preset/postset of places/transitions need to be inserted
    """
    return exec_utils.get_variant(variant).build(trace, sync_net, sync_im, sync_fm, parameters=parameters)


def get_h_value(solver: Any, variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> int:
    """
    Gets the heuristics value from the extended marking equation

    Parameters
    --------------
    solver
        Extended marking equation solver (class in this file)
    variant
        Variant of the algorithm to use, possible values:
        - Variants.CLASSIC
    parameters
        Possible parameters of the algorithm
    """
    return exec_utils.get_variant(variant).get_h_value(solver, parameters=parameters)

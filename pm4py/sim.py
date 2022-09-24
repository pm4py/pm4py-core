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
__doc__ = """
The ``pm4py.sim`` module contains the simulation algorithms offered in ``pm4py``
"""

from collections import Counter
from typing import Union, Tuple

from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree


def play_out(*args: Union[Tuple[PetriNet, Marking, Marking], dict, Counter, ProcessTree], **kwargs) -> EventLog:
    """
    Performs the playout of the provided model,
    i.e., gets a set of traces from the model.
    The function either takes a petri net, initial and final marking, or, a process tree as an input.

    :param args: model (Petri net with initial and final marking, or process tree)
    :param kwargs: dictionary containing the parameters of the playout
    :rtype: ``EventLog``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        log = pm4py.play_out(net, im, fm)

    """
    if len(args) == 3:
        from pm4py.objects.petri_net.obj import PetriNet
        if type(args[0]) is PetriNet:
            from pm4py.algo.simulation.playout.petri_net import algorithm
            return algorithm.apply(args[0], args[1], final_marking=args[2], **kwargs)
        elif isinstance(args[0], dict):
            from pm4py.algo.simulation.playout.dfg import algorithm as dfg_playout
            return dfg_playout.apply(args[0], args[1], args[2], **kwargs)
    elif len(args) == 1:
        from pm4py.objects.process_tree.obj import ProcessTree
        if type(args[0]) is ProcessTree:
            from pm4py.algo.simulation.playout.process_tree import algorithm
            return algorithm.apply(args[0], **kwargs)
    raise Exception("unsupported model for playout")


def generate_process_tree(**kwargs) -> ProcessTree:
    """
    Generates a process tree

    Reference paper:
    PTandLogGenerator: A Generator for Artificial Event Data

    :param kwargs: dictionary containing the parameters of the process tree generator algorithm
    :rtype: ``ProcessTree``

    .. code-block:: python3

        import pm4py

        process_tree = pm4py.generate_process_tree()
    """
    from pm4py.algo.simulation.tree_generator import algorithm
    return algorithm.apply(**kwargs)

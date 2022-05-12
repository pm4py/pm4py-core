__doc__ = """
We offer different simulation algorithms, that starting from a model, are able to produce an output that follows the model and the different rules that have been provided by the user.

* `Playout of a process model`_
* `Generation of a process model (process tree)`_

.. _Playout of a process model: pm4py.html#pm4py.sim.play_out
.. _Generation of a process model (process tree): pm4py.html#pm4py.sim.generate_process_tree

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
    """
    if len(args) == 3:
        from pm4py.objects.petri_net.obj import PetriNet
        if type(args[0]) is PetriNet:
            from pm4py.algo.simulation.playout.petri_net import algorithm
            return algorithm.apply(args[0], args[1], final_marking=args[2], **kwargs)
        elif isinstance(args[0], dict):
            from pm4py.objects.dfg.utils import dfg_playout
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

    :param kwargs: dictionary containing the parameters of the process tree generator algorithm
    :rtype: ``ProcessTree``
    """
    from pm4py.algo.simulation.tree_generator import algorithm
    return algorithm.apply(**kwargs)

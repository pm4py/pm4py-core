from pm4py.algo.simulation import playout

import importlib.util
if importlib.util.find_spec("tree_generator"):
    from pm4py.algo.simulation import tree_generator

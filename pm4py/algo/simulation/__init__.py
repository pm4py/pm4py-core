from pm4py.algo.simulation import playout

import pkgutil
if pkgutil.find_loader("tree_generator"):
    from pm4py.algo.simulation import tree_generator

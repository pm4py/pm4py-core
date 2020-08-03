from pm4py.simulation import playout, montecarlo, tree_playout
import pkgutil

# tree generation is possible only with scipy installed
if pkgutil.find_loader("scipy"):
    from pm4py.simulation import tree_generator

import importlib.util

if importlib.util.find_spec("matplotlib"):
    from pm4py.algo.comparison import petrinet

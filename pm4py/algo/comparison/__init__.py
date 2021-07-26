import pkgutil

if pkgutil.find_loader("matplotlib"):
    from pm4py.algo.comparison import petrinet

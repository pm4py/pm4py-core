import pkgutil

if pkgutil.find_loader("matplotlib"):
    # comparison required Matplotlib
    from pm4py.algo.enhancement.comparison import petrinet

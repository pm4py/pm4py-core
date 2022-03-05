import pkgutil

if pkgutil.find_loader("matplotlib"):
    from pm4py.algo.comparison import petrinet

import warnings

warnings.warn("The comparison package will be removed in a future release.")

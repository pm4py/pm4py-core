from pm4py.algo.transformation.log_to_features import algorithm, variants

import pkgutil

if pkgutil.find_loader("sklearn"):
    from pm4py.algo.transformation.log_to_features import util

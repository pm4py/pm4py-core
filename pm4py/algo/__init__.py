from pm4py.algo import discovery, conformance, reduction, analysis, evaluation, simulation, comparison, organizational_mining, transformation

import pkgutil

if pkgutil.find_loader("sklearn"):
    from pm4py.algo import decision_mining

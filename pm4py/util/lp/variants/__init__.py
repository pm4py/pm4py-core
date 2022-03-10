import pkgutil

if pkgutil.find_loader("pulp"):
    from pm4py.util.lp.variants import pulp_solver

if pkgutil.find_loader("scipy"):
    from pm4py.util.lp.variants import scipy_solver

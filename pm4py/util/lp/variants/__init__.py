import pkgutil

if pkgutil.find_loader("pulp"):
    from pm4py.util.lp.variants import pulp_solver

if pkgutil.find_loader("ortools"):
    from pm4py.util.lp.variants import ortools_solver

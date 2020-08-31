from pm4py.evaluation import generalization, precision, replay_fitness, simplicity, evaluator
import pkgutil

if pkgutil.find_loader("pyemd"):
    # import the EMD only if the pyemd package is installed
    from pm4py.evaluation import earth_mover_distance

if pkgutil.find_loader("networkx") and pkgutil.find_loader("sympy"):
    # import the Woflan package only if NetworkX and sympy are installed
    from pm4py.evaluation import soundness

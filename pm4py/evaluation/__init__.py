from pm4py.evaluation import generalization, precision, replay_fitness, simplicity, evaluator
import pkgutil

if pkgutil.find_loader("pyemd"):
    from pm4py.evaluation import earth_mover_distance

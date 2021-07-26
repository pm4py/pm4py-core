from pm4py.algo.evaluation import precision, replay_fitness, simplicity, generalization, algorithm
import pkgutil

if pkgutil.find_loader("pyemd"):
    # import the EMD only if the pyemd package is installed
    from pm4py.algo.evaluation import earth_mover_distance

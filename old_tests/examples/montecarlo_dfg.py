from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.dfg import factory as dfg_miner
from pm4py.objects.conversion.dfg import factory as dfg_conv_factory
from pm4py.algo.simulation.montecarlo import factory as montecarlo_simulation
from pm4py.algo.conformance.tokenreplay.algorithm import Variants
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    frequency_dfg = dfg_miner.apply(log, variant="frequency")
    net, im, fm = dfg_conv_factory.apply(frequency_dfg)
    # perform the Montecarlo simulation with the arrival rate inferred by the log (the simulation lasts 5 secs)
    log, res = montecarlo_simulation.apply(log, net, im, fm, parameters={"token_replay_variant": Variants.BACKWARDS, "enable_diagnostics": False, "max_thread_exec_time": 5})
    print("\n(Montecarlo - Petri net) case arrival ratio inferred from the log")
    print(res["median_cases_ex_time"])
    print(res["total_cases_time"])
    # perform the Montecarlo simulation with the arrival rate specified (the simulation lasts 5 secs)
    log, res = montecarlo_simulation.apply(log, net, im, fm, parameters={"token_replay_variant": Variants.BACKWARDS, "enable_diagnostics": False, "max_thread_exec_time": 5, "case_arrival_ratio": 60})
    print("\n(Montecarlo - Petri net) case arrival ratio specified by the user")
    print(res["median_cases_ex_time"])
    print(res["total_cases_time"])


if __name__ == "__main__":
    execute_script()

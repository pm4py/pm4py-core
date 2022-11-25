from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.simulation.montecarlo import algorithm as montecarlo_simulation
from pm4py.objects.conversion.process_tree import converter as process_tree_converter
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    process_tree = inductive_miner.apply(log)
    net, im, fm = process_tree_converter.apply(process_tree)
    # perform the Montecarlo simulation with the arrival rate inferred by the log (the simulation lasts 5 secs)
    parameters = {}
    parameters[montecarlo_simulation.Variants.PETRI_SEMAPH_FIFO.value.Parameters.PARAM_ENABLE_DIAGNOSTICS] = False
    parameters[montecarlo_simulation.Variants.PETRI_SEMAPH_FIFO.value.Parameters.PARAM_MAX_THREAD_EXECUTION_TIME] = 5
    log, res = montecarlo_simulation.apply(log, net, im, fm, parameters=parameters)
    print("\n(Montecarlo - Petri net) case arrival ratio inferred from the log")
    print(res["median_cases_ex_time"])
    print(res["total_cases_time"])
    # perform the Montecarlo simulation with the arrival rate specified (the simulation lasts 5 secs)
    parameters[montecarlo_simulation.Variants.PETRI_SEMAPH_FIFO.value.Parameters.PARAM_CASE_ARRIVAL_RATIO] = 60
    log, res = montecarlo_simulation.apply(log, net, im, fm, parameters=parameters)
    print("\n(Montecarlo - Petri net) case arrival ratio specified by the user")
    print(res["median_cases_ex_time"])
    print(res["total_cases_time"])


if __name__ == "__main__":
    execute_script()

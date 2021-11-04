from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.dfg import algorithm as dfg_miner
from pm4py.objects.conversion.dfg import converter as dfg_conv
from pm4py.algo.simulation.montecarlo import algorithm as montecarlo_simulation
from pm4py.algo.conformance.tokenreplay.algorithm import Variants
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    frequency_dfg = dfg_miner.apply(log, variant=dfg_miner.Variants.FREQUENCY)
    net, im, fm = dfg_conv.apply(frequency_dfg)
    # perform the Montecarlo simulation with the arrival rate inferred by the log (the simulation lasts 5 secs)
    parameters = {}
    parameters[
        montecarlo_simulation.Variants.PETRI_SEMAPH_FIFO.value.Parameters.TOKEN_REPLAY_VARIANT] = Variants.BACKWARDS
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

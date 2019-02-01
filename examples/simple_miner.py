import os

from pm4py.algo.discovery.simple.model.log import factory as simple_miner
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.petri.check_soundness import check_petri_wfnet_and_soundness


def execute_script():
    # loads the log
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))
    # apply the simple miner
    net, im, fm = simple_miner.apply(log, classic_output=True)
    # checks if the Petri net is a sound workflow net
    is_sound_wfnet = check_petri_wfnet_and_soundness(net)
    print("is_sound_wfnet = ", is_sound_wfnet)


if __name__ == "__main__":
    execute_script()

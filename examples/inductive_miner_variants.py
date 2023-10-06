import pm4py
import os
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.util.compression.dtypes import UVCL
from pm4py.algo.discovery.inductive.variants.imf import IMFUVCL
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"), return_legacy_log_object=False)
    variants = pm4py.get_variants(log)
    uvcl = UVCL()
    for var, occ in variants.items():
        uvcl[var] = occ
    parameters = {"noise_threshold": 0.2}
    imfuvcl = IMFUVCL(parameters)

    tree = imfuvcl.apply(IMDataStructureUVCL(uvcl), parameters=parameters)
    pm4py.view_process_tree(tree, format="svg")
    net, im, fm = pm4py.convert_to_petri_net(tree)
    pm4py.view_petri_net(net, im, fm, format="svg")


if __name__ == "__main__":
    execute_script()

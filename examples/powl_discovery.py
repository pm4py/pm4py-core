import pm4py
from examples import examples_conf
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from pm4py.visualization.powl.visualizer import POWLVisualizationVariants


def execute_script():
    log = pm4py.read_xes("../tests/input_data/helpdesk.xes.gz", return_legacy_log_object=True)

    # discovers the POWL model
    powl_model = pm4py.discover_powl(log, variant=POWLDiscoveryVariant.DYNAMIC_CLUSTERING, order_graph_filtering_threshold=0.6)

    # prints the repr of the POWL model
    print(powl_model)

    # views the POWL model on the screen
    pm4py.view_powl(powl_model, format=examples_conf.TARGET_IMG_FORMAT, variant_str="basic")
    pm4py.view_powl(powl_model, format=examples_conf.TARGET_IMG_FORMAT, variant_str="net")

    # converts the POWL model to a Petri net (which can be used for conformance checking)
    net, im, fm = pm4py.convert_to_petri_net(powl_model)
    pm4py.view_petri_net(net, im, fm, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.transition_system import algorithm as ts_discovery
from pm4py.visualization.transition_system import visualizer as ts_vis
import os


def execute_script():
    # log_path = "C:/Users/bas/Documents/tue/svn/private/logs/ilp_test_2_abcd_acbd.xes"
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    log = xes_importer.apply(log_path)
    ts = ts_discovery.apply(log)
    viz = ts_vis.apply(ts, parameters={ts_vis.Variants.VIEW_BASED.value.Parameters.FORMAT: "svg"})
    ts_vis.view(viz)


if __name__ == '__main__':
    execute_script()

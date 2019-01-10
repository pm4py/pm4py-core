from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.transition_system import factory as ts_factory
from pm4py.visualization.transition_system import factory as ts_vis_factory
from pm4py.algo.discovery.transition_system.parameters import PARAM_KEY_WINDOW
import os


def execute_script():
    # log_path = "C:/Users/bas/Documents/tue/svn/private/logs/ilp_test_2_abcd_acbd.xes"
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    log = xes_importer.import_log(log_path)
    ts = ts_factory.apply(log, parameters={PARAM_KEY_WINDOW: 2})
    viz = ts_vis_factory.apply(ts, parameters={"format": "svg"})
    ts_vis_factory.view(viz)


if __name__ == '__main__':
    execute_script()

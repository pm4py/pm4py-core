from pm4py import log as log_lib
from pm4py.algo.transition_system.versions import view_based as ts
from pm4py.models.transition_system import visualize as ts_viz

if __name__ == '__main__':
    log = log_lib.importing.xes.import_from_path_xes('C:/Users/bas/Documents/tue/svn/private/logs/ilp_test_2_abcd_acbd.xes')
    ts = ts.apply(log, parameters={ts.PARAM_KEY_VIEW: ts.VIEW_SEQUENCE, ts.PARAM_KEY_WINDOW: 3, ts.PARAM_KEY_DIRECTION: ts.DIRECTION_FORWARD})
    viz = ts_viz.graphviz.visualize(ts)
    viz.view()


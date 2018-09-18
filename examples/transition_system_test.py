import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.log.importer.xes import factory as xes_importer
from pm4py import log as log_lib
from pm4py.algo.transition_system import factory as ts_factory
from pm4py.models.transition_system import visualize as ts_viz
from pm4py.algo.transition_system.parameters import *

if __name__ == '__main__':
    #logPath = "C:/Users/bas/Documents/tue/svn/private/logs/ilp_test_2_abcd_acbd.xes"
    logPath = os.path.join("..","tests","inputData","running-example.xes")
    log = xes_importer.import_log(logPath)
    ts = ts_factory.apply(log, parameters={PARAM_KEY_WINDOW: 2})
    viz = ts_viz.graphviz.visualize(ts)
    viz.view()

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import pm4py
from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.transition_system import factory as ts_factory
from pm4py.visualization.transition_system import factory as ts_vis_factory
from pm4py.algo.discovery.transition_system.parameters import *

def execute_script():
    #logPath = "C:/Users/bas/Documents/tue/svn/private/logs/ilp_test_2_abcd_acbd.xes"
    logPath = os.path.join("..","tests","inputData","running-example.xes")
    log = xes_importer.import_log(logPath)
    ts = ts_factory.apply(log, parameters={PARAM_KEY_WINDOW: 2})
    viz = ts_vis_factory.apply(ts)
    viz.view()

if __name__ == '__main__':
    execute_script()
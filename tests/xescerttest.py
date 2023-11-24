import inspect
import os
import sys

from pm4py.algo.discovery.dfg import algorithm as dfg_algorithm
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import insert_classifier
from pm4py.util import constants, pandas_utils
from pm4py.visualization.dfg import visualizer as dfg_vis

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


def execute_script():
    log_input_directory = "xesinput"
    all_logs_names = os.listdir(log_input_directory)
    all_logs_names = [log for log in all_logs_names if ".xe" in log]

    for logName in all_logs_names:
        # logPath = os.path.join("..", "tests", "inputData", logName)
        log_path = log_input_directory + "\\" + logName
        log = xes_importer.apply(log_path)
        print("\n\n")
        print("log loaded")
        print("Number of traces - ", len(log))
        event_log = log_conversion.apply(log, variant=log_conversion.TO_EVENT_STREAM)
        print("Number of events - ", len(event_log))
        print("Classifiers ", log.classifiers)
        exp_log_name = "xescert_exportlogs" + "\\" + "exp_" + logName
        print("exporting log", exp_log_name)
        xes_exporter.apply(log, exp_log_name)
        print("exported log", exp_log_name)

        log, classifier_attr_key = insert_classifier.search_act_class_attr(log)

        classifiers = list(log.classifiers.keys())
        if classifier_attr_key is None and classifiers:
            try:
                print(classifiers)
                log, classifier_attr_key = insert_classifier.insert_activity_classifier_attribute(log, classifiers[0])
                print(classifier_attr_key)
            except:
                print("exception in handling classifier")

        if classifier_attr_key is None:
            classifier_attr_key = "concept:name"

        if len(event_log) > 0 and classifier_attr_key in event_log[0]:
            parameters = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: classifier_attr_key}

            dfg = dfg_algorithm.apply(log, parameters=parameters)
            gviz = dfg_vis.apply(dfg, log=log, variant="frequency", parameters=parameters)
            # dfg_vis.view(gviz)

            dfg_vis.save(gviz, "xescert_images\\" + logName.replace("xes", "png"))

        print("Reimporting log file just exported - ", exp_log_name)

        log = xes_importer.apply(exp_log_name)
        print("log loaded", exp_log_name)
        print("Number of traces - ", len(log))
        event_log = log_conversion.apply(log, variant=log_conversion.TO_EVENT_STREAM)
        print("Number of events - ", len(event_log))
        print("Classifiers ", log.classifiers)


if __name__ == "__main__":
    execute_script()

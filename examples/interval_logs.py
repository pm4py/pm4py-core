import os
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.conversion.lifecycle_log import factory as lifecycle_converter
from pm4py.objects.lifecycle_log.util import get_int_tree_attribute
from pm4py.util import constants
from pm4py.objects.log.util import xes
from pm4py.visualization.intervaltree import factory as int_tree_vis_factory
from pm4py.objects.lifecycle_log.util import lead_cycle_time_interval_logs


def execute_script():
    # import the BPI Challenge 2012 log that is a lifecycle log
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "bpic2012.xes.gz"), variant="nonstandard")
    # convert the BPI Challenge 2012 log to an interval log, including the estimated
    # business hours duration (standard hour 7-17, 6th and 7th day are wekeend)
    interval_log = lifecycle_converter.apply(log, variant=lifecycle_converter.TO_INTERVAL,
                                             parameters={"business_hours": True})
    # gets some interval trees trees on the intervals where some activities were activated
    # (more than one means at the same time the activity is deployed more than once)
    interval_log, activities_trees = get_int_tree_attribute.get_int_tree(interval_log, parameters={
        constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: xes.DEFAULT_NAME_KEY})
    # calculate the partial, incremental, lead and cycle time for the events of the log
    # and write it as attribute of the log
    interval_log = lead_cycle_time_interval_logs.assign_lead_cycle_time(interval_log)

    print(activities_trees.keys())
    # represents an interval tree related to the activity: W_Nabellen offertes
    gviz = int_tree_vis_factory.apply(activities_trees["W_Nabellen offertes"], parameters={"format": "svg"})
    int_tree_vis_factory.view(gviz)


if __name__ == "__main__":
    execute_script()

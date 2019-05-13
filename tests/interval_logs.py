import os
import unittest
from pm4py.objects.conversion.lifecycle_log import factory as lifecycle_converter
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.lifecycle_log.util import lead_cycle_time_interval_logs
from pm4py.util import constants
from pm4py.objects.log.util import xes
from pm4py.visualization.intervaltree import factory as int_tree_vis_factory
from pm4py.algo.other.intervaltree.builder import factory as int_tree_builder


class IntervalLogsTests(unittest.TestCase):
    def test_conversion(self):
        # import the BPI Challenge 2012 log that is a lifecycle log
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "bpic2012.xes.gz"), variant="nonstandard",
                                 parameters={"max_no_traces_to_import": 100})
        # convert the BPI Challenge 2012 log to an interval log, including the estimated
        # business hours duration (standard hour 7-17, 6th and 7th day are wekeend)
        interval_log = lifecycle_converter.apply(log, variant=lifecycle_converter.TO_INTERVAL,
                                                 parameters={"business_hours": True})
        # convert the log back to lifecycle
        log2 = lifecycle_converter.apply(log)
        del log
        del interval_log
        del log2

    def test_lead_cycle_time(self):
        # import the BPI Challenge 2012 log that is a lifecycle log
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "bpic2012.xes.gz"), variant="nonstandard",
                                 parameters={"max_no_traces_to_import": 100})
        # convert the BPI Challenge 2012 log to an interval log, including the estimated
        # business hours duration (standard hour 7-17, 6th and 7th day are wekeend)
        interval_log = lifecycle_converter.apply(log, variant=lifecycle_converter.TO_INTERVAL,
                                                 parameters={"business_hours": True})
        # calculate the partial, incremental, lead and cycle time for the events of the log
        # and write it as attribute of the log
        interval_log = lead_cycle_time_interval_logs.assign_lead_cycle_time(interval_log)
        del log
        del interval_log

    def test_itree_building(self):
        # import the BPI Challenge 2012 log that is a lifecycle log
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "bpic2012.xes.gz"), variant="nonstandard",
                                 parameters={"max_no_traces_to_import": 100})
        # convert the BPI Challenge 2012 log to an interval log, including the estimated
        # business hours duration (standard hour 7-17, 6th and 7th day are wekeend)
        interval_log = lifecycle_converter.apply(log, variant=lifecycle_converter.TO_INTERVAL,
                                                 parameters={"business_hours": True})
        # gets some interval trees trees on the intervals where some activities were activated
        # (more than one means at the same time the activity is deployed more than once)
        interval_log, activities_trees = int_tree_builder.apply(interval_log, parameters={
            constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: xes.DEFAULT_NAME_KEY})
        # .. and here on the resources
        interval_log, resources_trees = int_tree_builder.apply(interval_log, parameters={
            constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: xes.DEFAULT_RESOURCE_KEY, "insert_as_attribute": False})
        # represents an interval tree related to the activity: W_Nabellen offertes
        gviz = int_tree_vis_factory.apply(activities_trees["W_Nabellen offertes"], parameters={"format": "svg"})
        del log
        del interval_log
        del activities_trees
        del resources_trees
        del gviz

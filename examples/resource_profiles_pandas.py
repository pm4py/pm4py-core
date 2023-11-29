from pm4py.util import pandas_utils, constants
from pm4py.objects.log.util import dataframe_utils
import os
from pm4py.algo.organizational_mining.resource_profiles import algorithm


def execute_script():
    log = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "running-example.csv"))
    log = dataframe_utils.convert_timestamp_columns_in_df(log, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT, timest_columns=["time:timestamp"])
    # Metric RBI 1.1: Number of distinct activities done by a resource in a given time interval [t1, t2)
    print(algorithm.distinct_activities(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sara"))
    # Metric RBI 1.3: Fraction of completions of a given activity a, by a given resource r,
    # during a given time slot, [t1, t2), with respect to the total number of activity completions by resource r
    # during [t1, t2)
    print(algorithm.activity_frequency(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sara", "decide"))
    # Metric RBI 2.1: The number of activity instances completed by a given resource during a given time slot.
    print(algorithm.activity_completions(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sara"))
    # Metric RBI 2.2: The number of cases completed during a given time slot in which a given resource was involved.
    print(algorithm.case_completions(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Pete"))
    # Metric RBI 2.3: The fraction of cases completed during a given time slot in which a given resource was involved
    # with respect to the total number of cases completed during the time slot.
    print(algorithm.fraction_case_completions(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Pete"))
    # Metric RBI 2.4: The average number of activities started by a given resource but not completed at a moment in time.
    print(algorithm.average_workload(log, "2010-12-30 00:00:00", "2011-01-15 00:00:00", "Mike"))
    # Metric RBI 3.1: The fraction of active time during which a given resource is involved in more than one activity
    # with respect to the resource's active time.
    print(algorithm.multitasking(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Mike"))
    # Metric RBI 4.3: The average duration of instances of a given activity completed during a given time slot by
    # a given resource.
    print(algorithm.average_duration_activity(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sue", "examine thoroughly"))
    # Metric RBI 4.4: The average duration of cases completed during a given time slot in which a given resource was involved.
    print(algorithm.average_case_duration(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sue"))
    # Metric RBI 5.1: The number of cases completed during a given time slot in which two given resources were involved.
    print(algorithm.interaction_two_resources(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Mike", "Pete"))
    # Metric RBI 5.2: The fraction of resources involved in the same cases with a given resource during a given time slot
    # with respect to the total number of resources active during the time slot.
    print(algorithm.social_position(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sue"))


if __name__ == "__main__":
    execute_script()

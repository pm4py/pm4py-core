import pm4py
from pm4py.algo.transformation.log_to_target import algorithm as log_to_target


def execute_script():
    log = pm4py.read_xes("../tests/input_data/running-example.xes")
    rem_time_target, classes = log_to_target.apply(log, variant=log_to_target.Variants.REMAINING_TIME)
    print(rem_time_target)
    next_time_target, classes = log_to_target.apply(log, variant=log_to_target.Variants.NEXT_TIME)
    print(next_time_target)
    next_activity_target, next_activities = log_to_target.apply(log, variant=log_to_target.Variants.NEXT_ACTIVITY)
    print(next_activity_target)
    print(next_activities)


if __name__ == "__main__":
    execute_script()

from enum import Enum


class Outputs(Enum):
    OUTPUT_PLACES_INTERVAL_TREES = "places_interval_trees"
    OUTPUT_TRANSITIONS_INTERVAL_TREES = "transitions_interval_trees"
    OUTPUT_CASES_EX_TIME = "cases_ex_time"
    OUTPUT_MEDIAN_CASES_EX_TIME = "median_cases_ex_time"
    OUTPUT_CASE_ARRIVAL_RATIO = "input_case_arrival_ratio"
    OUTPUT_TOTAL_CASES_TIME = "total_cases_time"

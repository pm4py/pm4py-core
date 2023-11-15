import pandas as pd
from pm4py.util import constants

from pm4py.algo.discovery.correlation_mining import algorithm as correlation_miner
from pm4py.objects.log.util import dataframe_utils
from pm4py.statistics.sojourn_time.pandas import get as soj_time_get
from pm4py.statistics.start_activities.pandas import get as sa_get
from pm4py.statistics.end_activities.pandas import get as ea_get
from examples import examples_conf

from pm4py.visualization.dfg import visualizer as dfg_vis


def execute_script():
    df = pd.read_csv("../tests/input_data/interval_event_log.csv")
    df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format="ISO8601")
    act_count = dict(df["concept:name"].value_counts())
    parameters = {}
    parameters[constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY] = "start_timestamp"
    parameters[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = "time:timestamp"
    parameters["format"] = examples_conf.TARGET_IMG_FORMAT
    start_activities = sa_get.get_start_activities(df, parameters=parameters)
    end_activities = ea_get.get_end_activities(df, parameters=parameters)
    parameters["start_activities"] = start_activities
    parameters["end_activities"] = end_activities
    soj_time = soj_time_get.apply(df, parameters=parameters)
    dfg, performance_dfg = correlation_miner.apply(df, variant=correlation_miner.Variants.CLASSIC,
                                                   parameters=parameters)
    gviz_freq = dfg_vis.apply(dfg, activities_count=act_count, soj_time=soj_time, variant=dfg_vis.Variants.FREQUENCY,
                              parameters=parameters)
    dfg_vis.view(gviz_freq)
    gviz_perf = dfg_vis.apply(performance_dfg, activities_count=act_count, soj_time=soj_time,
                              variant=dfg_vis.Variants.PERFORMANCE,
                              parameters=parameters)
    dfg_vis.view(gviz_perf)


if __name__ == "__main__":
    execute_script()

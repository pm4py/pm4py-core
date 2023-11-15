import os

import pandas as pd

from pm4py.util import constants
from pm4py.statistics.attributes.pandas import get as attr_get
from pm4py.visualization.graphs import visualizer
from examples import examples_conf


def execute_script():
    df = pd.read_csv(os.path.join("..", "tests", "input_data", "receipt.csv"))
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"], utc=True, format="ISO8601")
    # plots the distribution of the events over the days of a month
    x0, y0 = attr_get.get_events_distribution(df, distr_type="days_month")
    gviz = visualizer.apply(x0, y0, variant=visualizer.Variants.BARPLOT,
                            parameters={"format": examples_conf.TARGET_IMG_FORMAT, "title": "Distribution of the Events over the Days of a Month",
                                        "x_axis": "Day of month", "y_axis": "Number of Events"})
    visualizer.view(gviz)
    # plots the distribution of the events over the months
    x1, y1 = attr_get.get_events_distribution(df, distr_type="months")
    gviz = visualizer.apply(x1, y1, variant=visualizer.Variants.BARPLOT,
                            parameters={"format": examples_conf.TARGET_IMG_FORMAT, "title": "Distribution of the Events over the Months",
                                        "x_axis": "Month", "y_axis": "Number of Events"})
    visualizer.view(gviz)
    # plots the distribution of the events over the years
    x2, y2 = attr_get.get_events_distribution(df, distr_type="years")
    gviz = visualizer.apply(x2, y2, variant=visualizer.Variants.BARPLOT,
                            parameters={"format": examples_conf.TARGET_IMG_FORMAT, "title": "Distribution of the Events over the Years",
                                        "x_axis": "Year", "y_axis": "Number of Events"})
    visualizer.view(gviz)
    # plots the distribution of the events over the hours (of the day)
    x3, y3 = attr_get.get_events_distribution(df, distr_type="hours")
    gviz = visualizer.apply(x3, y3, variant=visualizer.Variants.BARPLOT,
                            parameters={"format": examples_conf.TARGET_IMG_FORMAT, "title": "Distribution of the Events over the Hours",
                                        "x_axis": "Hour (of day)", "y_axis": "Number of Events"})
    visualizer.view(gviz)
    # plots the distribution of the events over the days of the week
    x4, y4 = attr_get.get_events_distribution(df, distr_type="days_week")
    gviz = visualizer.apply(x4, y4, variant=visualizer.Variants.BARPLOT,
                            parameters={"format": examples_conf.TARGET_IMG_FORMAT, "title": "Distribution of the Events over the Days of a Week",
                                        "x_axis": "Day of the Week", "y_axis": "Number of Events"})
    visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()

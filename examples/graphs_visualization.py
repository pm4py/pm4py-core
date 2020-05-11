import os

from pm4py.statistics.attributes.log import get as attributes_filter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.statistics.traces.log import case_statistics
from pm4py.visualization.graphs import visualizer as graphs_visualizer


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))

    # visualize case duration graph
    x_cases, y_cases = case_statistics.get_kde_caseduration(log)
    graph_cases = graphs_visualizer.apply(x_cases, y_cases, variant=graphs_visualizer.Variants.CASES,
                                          parameters={graphs_visualizer.Variants.CASES.value.Parameters.FORMAT: "svg"})
    graphs_visualizer.view(graph_cases)

    # visualize events over time graph
    x_dates, y_dates = attributes_filter.get_kde_date_attribute(log)
    graph_dates = graphs_visualizer.apply(x_dates, y_dates, variant=graphs_visualizer.Variants.DATES,
                                          parameters={graphs_visualizer.Variants.DATES.value.Parameters.FORMAT: "svg"})
    graphs_visualizer.view(graph_dates)


if __name__ == "__main__":
    execute_script()

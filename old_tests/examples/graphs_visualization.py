import os

from pm4py.statistics.attributes.log import get as attributes_filter
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.statistics.traces.log import case_statistics
from pm4py.visualization.graphs import factory as graphs_factory


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))

    # visualize case duration graph
    x_cases, y_cases = case_statistics.get_kde_caseduration(log)
    graph_cases = graphs_factory.apply(x_cases, y_cases, variant="cases", parameters={"format": "svg"})
    graphs_factory.view(graph_cases)

    # visualize events over time graph
    x_dates, y_dates = attributes_filter.get_kde_date_attribute(log)
    graph_dates = graphs_factory.apply(x_dates, y_dates, variant="dates", parameters={"format": "svg"})
    graphs_factory.view(graph_dates)


if __name__ == "__main__":
    execute_script()

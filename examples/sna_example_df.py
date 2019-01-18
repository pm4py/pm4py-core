import os

from pm4py.algo.enhancement.sna.metrics.handover import factory as handover_of_work
from pm4py.algo.enhancement.sna.metrics.real_handover import factory as real_handover_of_work
from pm4py.algo.enhancement.sna.metrics.similar_activities import factory as similar_activities
from pm4py.algo.enhancement.sna.transformer.pandas import factory as sna_transformer
from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.visualization.sna import factory as sna_vis_factory


def execute_script():
    # loads the dataframe from the CSV file
    csv_path = os.path.join("..", "tests", "input_data", "running-example.csv")
    df = csv_import_adapter.import_dataframe_from_path(csv_path)
    # calculates the Matrix Container object
    mco = sna_transformer.apply(df)
    # calculates the Handover of Work matrix
    hw_matrix = handover_of_work.apply(mco)
    # calculates the Similar Activities matrix
    sim_act_matrix = similar_activities.apply(mco)
    # shows the Handover of Work graph
    gviz = sna_vis_factory.apply(mco, hw_matrix, parameters={"format": "svg"})
    sna_vis_factory.view(gviz)
    # shows the Similar Activities graph
    gviz = sna_vis_factory.apply(mco, sim_act_matrix, parameters={"format": "svg", "threshold": 0.0})
    sna_vis_factory.view(gviz)
    # calculates the Real Handover of Work matrix
    real_hw_matrix = real_handover_of_work.apply(mco, parameters={"format": "svg"})
    gviz = sna_vis_factory.apply(mco, real_hw_matrix)


if __name__ == "__main__":
    execute_script()

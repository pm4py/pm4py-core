import os

from pm4py.algo.enhancement.sna.metrics.handover import factory as handover_of_work
from pm4py.algo.enhancement.sna.metrics.similar_activities import factory as similar_activities
from pm4py.algo.enhancement.sna.transformer.tracelog import factory as sna_transformer
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.sna import factory as sna_vis_factory


def execute_script():
    # loads the log from XES file
    log_path = os.path.join("..", "tests", "input_data", "receipt.xes")
    log = xes_importer.apply(log_path)
    # calculates the Matrix Container object
    mco = sna_transformer.apply(log)
    # calculates the Handover of Work matrix
    hw_matrix = handover_of_work.apply(mco)
    # calculates the Similar Activities matrix
    sim_act_matrix = similar_activities.apply(mco)
    # shows the Handover of Work graph
    gviz = sna_vis_factory.apply(mco, hw_matrix, variant="pyvis")
    sna_vis_factory.view(gviz, variant="pyvis")
    # shows the Similar Activities graph
    gviz = sna_vis_factory.apply(mco, sim_act_matrix, parameters={"threshold": 0.0}, variant="pyvis")
    sna_vis_factory.view(gviz, variant="pyvis")


if __name__ == "__main__":
    execute_script()

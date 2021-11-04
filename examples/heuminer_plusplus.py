import pm4py
from pm4py.algo.discovery.heuristics.variants import plusplus
from pm4py.visualization.heuristics_net import visualizer
from pm4py.visualization.petri_net import visualizer as pn_visualizer
import pandas as pd


def execute_script():
    df = pd.read_csv("../tests/input_data/interval_event_log.csv")
    df = pm4py.format_dataframe(df)
    log = pm4py.read_xes("../tests/input_data/interval_event_log.xes")
    heu_net = plusplus.apply_heu(log, parameters={"heu_net_decoration": "performance"})
    heu_net_2 = plusplus.apply_heu_pandas(df, parameters={"heu_net_decoration": "performance"})
    gviz = visualizer.apply(heu_net, parameters={"format": "svg"})
    visualizer.view(gviz)
    gviz2 = visualizer.apply(heu_net_2, parameters={"format": "svg"})
    visualizer.view(gviz2)
    net1, im1, fm1 = plusplus.apply(log)
    net2, im2, fm2 = plusplus.apply(log)
    gviz3 = pn_visualizer.apply(net1, im1, fm1, parameters={"format": "svg"})
    pn_visualizer.view(gviz3)
    gviz4 = pn_visualizer.apply(net2, im2, fm2, parameters={"format": "svg"})
    pn_visualizer.view(gviz4)


if __name__ == "__main__":
    execute_script()

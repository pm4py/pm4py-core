from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.objects.log.importer.xes import importer
from pm4py.visualization.petrinet import visualizer


def sample():
    log = importer.apply('../tests/input_data/running-example.xes')
    net, initial_marking, final_marking = alpha_miner.apply(log)
    gviz = visualizer.apply(net, initial_marking, final_marking)
    visualizer.view(gviz)


if __name__ == '__main__':
    sample()

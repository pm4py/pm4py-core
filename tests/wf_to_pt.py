import pm4py
from pm4py.objects.conversion.wf_net.variants import to_process_tree as converter
log = pm4py.read_xes('input_data/running-example.xes')
net, im, fm = pm4py.discover_petri_net_inductive(log)
pm4py.view_petri_net(net, im, fm, format="svg")
tree = converter.apply(net)
print(tree)
pm4py.view_process_tree(tree, format="svg")
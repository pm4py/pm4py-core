import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import pm4py.algo.alignments as align
import pm4py.evaluation as eval
import pm4py.models.petri as petri
from pm4py import log as log_lib

if __name__ == '__main__':
    # log = log_lib.importer.xes.import_from_path_xes('C:/Users/bas/Desktop/reviewing.xes')
    log = log_lib.importer.xes.import_from_file_xes('C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n05.xes')
    # net, marking = petri.importer.import_petri_from_pnml('C:/Users/bas/Desktop/reviewingPnml2.pnml')
    net, marking = petri.importer.pnml.import_petri_from_pnml('C:/Users/bas/Desktop/a32.pnml')
    # net, imarking = inductive.apply(log)
    # viz = petri.visualize.graphviz_visualization(net)
    # viz.view()
    fmarking = petri.petrinet.Marking()
    for p in net.places:
        if len(p.out_arcs) == 0:
            fmarking[p] = 1

    model_cost_function = dict()
    sync_cost_function = dict()
    for t in net.transitions:
        if t.label is not None:
            model_cost_function[t] = 1000
            sync_cost_function[t] = 0
        else:
            model_cost_function[t] = 1
    '''
    for t in log:
        trace_costs = list(map(lambda e: 1000, t))
        params = dict()
        params[align.versions.state_equation_a_star.PARAM_ACTIVITY_KEY] = log_lib.util.xes.DEFAULT_NAME_KEY
        params[align.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION] = model_cost_function
        params[align.versions.state_equation_a_star.PARAM_TRACE_COST_FUNCTION] = trace_costs
        params[align.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION] = sync_cost_function
        print(align.versions.state_equation_a_star.apply(t, net, marking, fmarking, parameters=params))
    '''

    alignments = eval.replay_fitness.versions.alignment_based.apply(log, net, marking, fmarking, {
        eval.replay_fitness.versions.alignment_based.PARAM_ACTIVITY_KEY: log_lib.util.xes.DEFAULT_NAME_KEY})
    for a in alignments:
        if a['fitness'] < 1.0:
            print(a)

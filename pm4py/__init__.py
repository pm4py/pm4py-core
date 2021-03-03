import sys
import time

from pm4py import util, objects, statistics, algo, visualization, evaluation, simulation
from pm4py.analysis import check_soundness
from pm4py.conformance import conformance_tbr, conformance_alignments, evaluate_fitness_tbr, \
    evaluate_fitness_alignments, evaluate_precision_tbr, \
    evaluate_precision_alignments, soundness_woflan
from pm4py.convert import convert_to_event_log, convert_to_event_stream, convert_to_dataframe, convert_to_bpmn, \
    convert_to_petri_net, convert_to_process_tree
from pm4py.discovery import discover_petri_net_alpha, discover_petri_net_alpha_plus, discover_petri_net_heuristics, \
    discover_petri_net_inductive, discover_tree_inductive, discover_heuristics_net, discover_dfg
from pm4py.filtering import filter_start_activities, filter_end_activities, filter_attribute_values, filter_variants, \
    filter_variants_percentage, filter_directly_follows_relation, filter_time_range, filter_trace_attribute, \
    filter_eventually_follows_relation, filter_event_attribute_values, filter_trace_attribute_values
from pm4py.hof import filter_log, filter_trace, sort_trace, sort_log
# Keep meta variables accessible at top-level.
from pm4py.meta import __name__, __version__, __doc__, __author__, __author_email__, \
    __maintainer__, __maintainer_email__
from pm4py.read import read_xes, read_csv, read_petri_net, read_process_tree, read_dfg, \
    read_bpmn
from pm4py.stats import get_start_activities, get_end_activities, get_attributes, get_attribute_values, get_variants, \
    get_trace_attributes, get_variants_as_tuples
from pm4py.utils import format_dataframe
from pm4py.vis import view_petri_net, save_vis_petri_net, view_dfg, save_vis_dfg, view_process_tree, \
    save_vis_process_tree, \
    view_heuristics_net, save_vis_heuristics_net, view_bpmn, save_vis_bpmn
from pm4py.write import write_xes, write_csv, write_petri_net, write_process_tree, write_dfg, write_bpmn

time.clock = time.process_time

# this package is available only for Python >= 3.5
if sys.version_info >= (3, 5):
    from pm4py import streaming

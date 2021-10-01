'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import sys
import time

from pm4py import util, objects, statistics, algo, visualization
from pm4py.analysis import check_soundness, solve_marking_equation, solve_extended_marking_equation, \
    construct_synchronous_product_net
from pm4py.conformance import conformance_diagnostics_token_based_replay, conformance_diagnostics_alignments, \
    fitness_token_based_replay, \
    fitness_alignments, precision_token_based_replay, \
    precision_alignments, conformance_alignments, conformance_tbr, evaluate_precision_alignments, \
    evaluate_precision_tbr, evaluate_fitness_tbr, evaluate_fitness_alignments, conformance_diagnostics_footprints, \
    fitness_footprints, precision_footprints, check_is_fitting
from pm4py.convert import convert_to_event_log, convert_to_event_stream, convert_to_dataframe, convert_to_bpmn, \
    convert_to_petri_net, convert_to_process_tree
from pm4py.discovery import discover_petri_net_alpha, discover_petri_net_alpha_plus, discover_petri_net_heuristics, \
    discover_petri_net_inductive, discover_tree_inductive, discover_process_tree_inductive, discover_heuristics_net, \
    discover_dfg, discover_footprints, discover_eventually_follows_graph, discover_directly_follows_graph, discover_bpmn_inductive, \
    discover_performance_dfg
from pm4py.filtering import filter_start_activities, filter_end_activities, filter_attribute_values, filter_variants, \
    filter_variants_percentage, filter_directly_follows_relation, filter_time_range, filter_trace_attribute, \
    filter_eventually_follows_relation, filter_event_attribute_values, filter_trace_attribute_values, \
    filter_between, filter_case_size, filter_case_performance, filter_activities_rework, filter_paths_performance, \
    filter_variants_by_coverage_percentage, filter_variants_top_k
from pm4py.hof import filter_log, filter_trace, sort_trace, sort_log
from pm4py.meta import __name__, __version__, __doc__, __author__, __author_email__, \
    __maintainer__, __maintainer_email__
from pm4py.read import read_xes, read_petri_net, read_process_tree, read_dfg, \
    read_bpmn, read_pnml, read_ptml
from pm4py.sim import play_out, generate_process_tree
from pm4py.stats import get_start_activities, get_end_activities, get_event_attributes, get_attributes, get_event_attribute_values, get_attribute_values, get_variants, \
    get_trace_attributes, get_variants_as_tuples, get_trace_attribute_values, get_case_arrival_average, \
    get_minimum_self_distances, get_minimum_self_distance_witnesses, \
    get_case_arrival_average, get_rework_cases_per_activity, get_case_overlap, get_cycle_time, \
    get_all_case_durations, get_case_duration
from pm4py.utils import format_dataframe, parse_process_tree, serialize, deserialize, set_classifier
from pm4py.vis import view_petri_net, save_vis_petri_net, view_dfg, save_vis_dfg, view_process_tree, \
    save_vis_process_tree, \
    view_heuristics_net, save_vis_heuristics_net, view_bpmn, save_vis_bpmn, view_sna, save_vis_sna,\
    view_dotted_chart, save_vis_dotted_chart, view_performance_spectrum, save_vis_performance_spectrum, view_case_duration_graph, view_events_per_time_graph, save_vis_case_duration_graph, save_vis_events_per_time_graph, view_events_distribution_graph, save_vis_events_distribution_graph, view_performance_dfg, save_vis_performance_dfg
from pm4py.write import write_xes, write_petri_net, write_process_tree, write_dfg, write_bpmn, write_pnml, write_ptml
from pm4py.org import discover_handover_of_work_network, discover_activity_based_resource_similarity, discover_subcontracting_network, discover_working_together_network, discover_organizational_roles
from pm4py.ml import split_train_test, get_prefixes_from_log

time.clock = time.process_time

# this package is available only for Python >= 3.5
if sys.version_info >= (3, 5):
    from pm4py import streaming

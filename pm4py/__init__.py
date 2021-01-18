VERSION = '2.1.4'

import logging
import pkgutil
import sys
import time

time.clock = time.process_time

from pm4py import util, objects, statistics, algo, visualization, evaluation, simulation

if pkgutil.find_loader("scipy"):
    pass
else:
    logging.error("scipy is not available. This can lead some features of PM4Py to not work correctly!")

if pkgutil.find_loader("sklearn"):
    pass
else:
    logging.error("scikit-learn is not available. This can lead some features of PM4Py to not work correctly!")

if pkgutil.find_loader("networkx"):
    pass
else:
    logging.error("networkx is not available. This can lead some features of PM4Py to not work correctly!")

if pkgutil.find_loader("matplotlib"):
    pass
else:
    logging.error("matplotlib is not available. This can lead some features of PM4Py to not work correctly!")

if pkgutil.find_loader("lxml"):
    pass
else:
    logging.error("lxml is not available. This can lead some features of PM4Py to not work correctly!")

if pkgutil.find_loader("pandas"):
    pass
else:
    logging.error("pandas is not available. This can lead some features of PM4Py to not work correctly!")

if pkgutil.find_loader("pulp"):
    pass
else:
    logging.error("pulp is not available. This can lead some features of PM4Py to not work correctly!")

if pkgutil.find_loader("graphviz"):
    pass
else:
    logging.error("graphviz is not available. This can lead some features of PM4Py to not work correctly!")

if pkgutil.find_loader("intervaltree"):
    pass
else:
    logging.error("intervaltree is not available. This can lead some features of PM4Py to not work correctly!")

__version__ = VERSION
__doc__ = "Process Mining for Python (PM4Py)"
__author__ = 'Fraunhofer Institute for Applied Technology'
__author_email__ = 'pm4py@fit.fraunhofer.de'
__maintainer__ = 'Fraunhofer Institute for Applied Technology'
__maintainer_email__ = "pm4py@fit.fraunhofer.de"

from pm4py.read import read_xes, read_csv, read_petri_net, read_process_tree, read_dfg, \
    read_bpmn
from pm4py.write import write_xes, write_csv, write_petri_net, write_process_tree, write_dfg, write_bpmn
from pm4py.discovery import discover_petri_net_alpha, discover_petri_net_alpha_plus, discover_petri_net_heuristics, \
    discover_petri_net_inductive, discover_tree_inductive, discover_heuristics_net, discover_dfg
from pm4py.conformance import conformance_tbr, conformance_alignments, evaluate_fitness_tbr, \
    evaluate_fitness_alignments, evaluate_precision_tbr, \
    evaluate_precision_alignments, soundness_woflan
from pm4py.vis import view_petri_net, save_vis_petri_net, view_dfg, save_vis_dfg, view_process_tree, \
    save_vis_process_tree, \
    view_heuristics_net, save_vis_heuristics_net, view_bpmn, save_vis_bpmn
from pm4py.filtering import filter_start_activities, filter_end_activities, filter_attribute_values, filter_variants, \
    filter_variants_percentage, filter_directly_follows_relation, filter_time_range, filter_trace_attribute, \
    filter_eventually_follows_relation, filter_event_attribute_values, filter_trace_attribute_values
from pm4py.stats import get_start_activities, get_end_activities, get_attributes, get_attribute_values, get_variants, \
    get_trace_attributes
from pm4py.convert import convert_to_event_log, convert_to_event_stream, convert_to_dataframe, convert_to_bpmn, \
    convert_to_petri_net, convert_to_process_tree
from pm4py.utils import format_dataframe
from pm4py.hof import filter_log, filter_trace, sort_trace, sort_log

# this package is available only for Python >= 3.5
if sys.version_info >= (3, 5):
    from pm4py import streaming

    if pkgutil.find_loader("sympy"):
        pass
    else:
        logging.error("sympy is not available. This can lead some features of PM4Py to not work correctly!")

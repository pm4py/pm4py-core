import logging
import pkgutil
import time

time.clock = time.process_time

try:
    import pm4pycvxopt
except:
    pass

from pm4py import util, objects, statistics, algo, visualization, evaluation, streaming, simulation

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
    import matplotlib
else:
    logging.error("matplotlib is not available. This can lead some features of PM4Py to not work correctly!")

__version__ = '1.4.1.1'
__doc__ = "Process Mining for Python (PM4Py)"
__author__ = 'Fraunhofer Institute for Applied Technology'
__author_email__ = 'pm4py@fit.fraunhofer.de'
__maintainer__ = 'Fraunhofer Institute for Applied Technology'
__maintainer_email__ = "pm4py@fit.fraunhofer.de"

from pm4py.read import read_xes, read_csv, read_petri_net, read_process_tree, read_dfg, format_dataframe, \
    convert_to_event_log, convert_to_event_stream, convert_to_dataframe
from pm4py.write import write_xes, write_csv, write_petri_net, write_process_tree, write_dfg
from pm4py.discovery import discover_petri_net_alpha, discover_petri_net_alpha_plus, discover_petri_net_heuristics, \
    discover_petri_net_inductive, discover_tree_inductive, discover_heuristics_net, discover_dfg
from pm4py.conformance import conformance_tbr, conformance_alignments, evaluate_fitness_tbr, \
    evaluate_fitness_alignments, evaluate_precision_tbr, \
    evaluate_precision_alignments
from pm4py.vis import view_petri_net, save_vis_petri_net, view_dfg, save_vis_dfg, view_process_tree, \
    save_vis_process_tree, \
    view_heuristics_net, save_vis_heuristics_net
from pm4py.filtering import filter_start_activities, filter_end_activities, filter_attribute_values, filter_variants, \
    filter_variants_percentage, filter_paths, filter_timestamp
from pm4py.stats import get_start_activities, get_end_activities, get_attributes, get_attribute_values, get_variants

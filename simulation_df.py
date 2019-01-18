import os

from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.algo.filtering.pandas.attributes import attributes_filter
from pm4py.algo.simulation.simple.model.pandas import factory as model_factory
from pm4py.objects.log.importer.csv.versions import pandas_df_imp
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.objects.stochastic_petri import map as stochastic_map
from pm4py.objects.stochastic_petri.lp_perf_bounds import LpPerfBounds
from pm4py.statistics.traces.pandas.case_arrival import get_case_arrival_avg
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_decorations_from_dfg_spaths_acticount
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_shortest_paths

parameters = {}

log_name = os.path.join("tests", "input_data", "running-example.csv")
parameters[PARAMETER_CONSTANT_CASEID_KEY] = CASE_CONCEPT_NAME
parameters[PARAMETER_CONSTANT_ACTIVITY_KEY] = DEFAULT_NAME_KEY
parameters[PARAMETER_CONSTANT_TIMESTAMP_KEY] = DEFAULT_TIMESTAMP_KEY

parameters[PARAMETER_CONSTANT_ATTRIBUTE_KEY] = parameters[PARAMETER_CONSTANT_ACTIVITY_KEY]
CASEID_GLUE = parameters[PARAMETER_CONSTANT_CASEID_KEY]
ACTIVITY_KEY = parameters[PARAMETER_CONSTANT_ACTIVITY_KEY]
TIMEST_KEY = parameters[PARAMETER_CONSTANT_TIMESTAMP_KEY]

df = pandas_df_imp.import_dataframe_from_path(log_name)
# obtain a simple, sound workflow net, containing only visibile unique transitions,
# applying the Alpha Miner to some of the top variants (methods by Ale)
net, initial_marking, final_marking = model_factory.apply(df, classic_output=True)
# visualize the output Petri net
gviz = pn_vis_factory.apply(net, initial_marking, final_marking)
pn_vis_factory.view(gviz)
# gets the average time between cases starts
avg_time_starts = get_case_arrival_avg(df)
print("avg_time_starts=", avg_time_starts)
# gets the aggregated statistics calculated on the DFG graph and the Petri net
activities_count = attributes_filter.get_attribute_values(df, attribute_key=ACTIVITY_KEY)
[dfg_frequency, dfg_performance] = df_statistics.get_dfg_graph(df, measure="both",
                                                               perf_aggregation_key="median",
                                                               case_id_glue=CASEID_GLUE, activity_key=ACTIVITY_KEY,
                                                               timestamp_key=TIMEST_KEY)
spaths = get_shortest_paths(net)
aggregated_statistics = get_decorations_from_dfg_spaths_acticount(net, dfg_performance,
                                                                  spaths,
                                                                  activities_count,
                                                                  variant="performance")
# gets the stochastic distribution associated to the Petri net and the dataframe
smap = stochastic_map.get_map_exponential_from_aggstatistics(aggregated_statistics)
print("smap=", smap)
perf_bound_obj = LpPerfBounds(net, initial_marking, final_marking, smap, avg_time_starts)
net1, imarking1, fmarking1 = perf_bound_obj.get_net()
gviz = pn_vis_factory.apply(net1, imarking1, fmarking1)
pn_vis_factory.view(gviz)

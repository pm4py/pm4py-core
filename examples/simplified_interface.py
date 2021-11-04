import os

import pm4py
import pandas as pd

def execute_script():
    ENABLE_VISUALIZATION = True

    # reads a XES into an event log
    log1 = pm4py.read_xes("../tests/input_data/running-example.xes")

    # reads a CSV into a dataframe
    df = pd.read_csv("../tests/input_data/running-example.csv")
    # formats the dataframe with the mandatory columns for process mining purposes
    df = pm4py.format_dataframe(df, case_id="case:concept:name", activity_key="concept:name",
                                timestamp_key="time:timestamp")
    # converts the dataframe to an event log
    log2 = pm4py.convert_to_event_log(df)

    # converts the log read from XES into a stream and dataframe respectively
    stream1 = pm4py.convert_to_event_stream(log1)
    df2 = pm4py.convert_to_dataframe(log1)

    # writes the log1 to a XES file
    pm4py.write_xes(log1, "ru1.xes")

    dfg, dfg_sa, dfg_ea = pm4py.discover_dfg(log1)
    petri_alpha, im_alpha, fm_alpha = pm4py.discover_petri_net_alpha(log1)
    petri_inductive, im_inductive, fm_inductive = pm4py.discover_petri_net_inductive(log1)
    petri_heuristics, im_heuristics, fm_heuristics = pm4py.discover_petri_net_heuristics(log1)
    tree_inductive = pm4py.discover_process_tree_inductive(log1)
    heu_net = pm4py.discover_heuristics_net(log1)

    pm4py.write_dfg(dfg, dfg_sa, dfg_ea, "ru_dfg.dfg")
    pm4py.write_pnml(petri_alpha, im_alpha, fm_alpha, "ru_alpha.pnml")
    pm4py.write_pnml(petri_inductive, im_inductive, fm_inductive, "ru_inductive.pnml")
    pm4py.write_pnml(petri_heuristics, im_heuristics, fm_heuristics, "ru_heuristics.pnml")
    pm4py.write_ptml(tree_inductive, "ru_inductive.ptml")

    dfg, dfg_sa, dfg_ea = pm4py.read_dfg("ru_dfg.dfg")
    petri_alpha, im_alpha, fm_alpha = pm4py.read_pnml("ru_alpha.pnml")
    petri_inductive, im_inductive, fm_inductive = pm4py.read_pnml("ru_inductive.pnml")
    petri_heuristics, im_heuristics, fm_heuristics = pm4py.read_pnml("ru_heuristics.pnml")
    tree_inductive = pm4py.read_ptml("ru_inductive.ptml")

    pm4py.save_vis_petri_net(petri_alpha, im_alpha, fm_alpha, "ru_alpha.png")
    pm4py.save_vis_petri_net(petri_inductive, im_inductive, fm_inductive, "ru_inductive.png")
    pm4py.save_vis_petri_net(petri_heuristics, im_heuristics, fm_heuristics, "ru_heuristics.png")
    pm4py.save_vis_process_tree(tree_inductive, "ru_inductive_tree.png")
    pm4py.save_vis_heuristics_net(heu_net, "ru_heunet.png")
    pm4py.save_vis_dfg(dfg, dfg_sa, dfg_ea, "ru_dfg.png")

    pm4py.save_vis_events_per_time_graph(log1, "ev_time.png")
    pm4py.save_vis_case_duration_graph(log1, "cd.png")
    pm4py.save_vis_dotted_chart(log1, "dotted_chart.png")
    pm4py.save_vis_performance_spectrum(log1, ["register request", "decide"], "ps.png")

    if ENABLE_VISUALIZATION:
        pm4py.view_petri_net(petri_alpha, im_alpha, fm_alpha, format="svg")
        pm4py.view_petri_net(petri_inductive, im_inductive, fm_inductive, format="svg")
        pm4py.view_petri_net(petri_heuristics, im_heuristics, fm_heuristics, format="svg")
        pm4py.view_process_tree(tree_inductive, format="svg")
        pm4py.view_heuristics_net(heu_net, format="svg")
        pm4py.view_dfg(dfg, dfg_sa, dfg_ea, format="svg")

    aligned_traces = pm4py.conformance_diagnostics_alignments(log1, petri_inductive, im_inductive, fm_inductive)
    replayed_traces = pm4py.conformance_diagnostics_token_based_replay(log1, petri_inductive, im_inductive, fm_inductive)

    fitness_tbr = pm4py.fitness_token_based_replay(log1, petri_inductive, im_inductive, fm_inductive)
    print("fitness_tbr", fitness_tbr)
    fitness_align = pm4py.fitness_alignments(log1, petri_inductive, im_inductive, fm_inductive)
    print("fitness_align", fitness_align)
    precision_tbr = pm4py.precision_token_based_replay(log1, petri_inductive, im_inductive, fm_inductive)
    print("precision_tbr", precision_tbr)
    precision_align = pm4py.precision_alignments(log1, petri_inductive, im_inductive, fm_inductive)
    print("precision_align", precision_align)

    print("log start activities = ", pm4py.get_start_activities(log2))
    print("df start activities = ", pm4py.get_start_activities(df2))
    print("log end activities = ", pm4py.get_end_activities(log2))
    print("df end activities = ", pm4py.get_end_activities(df2))
    print("log attributes = ", pm4py.get_event_attributes(log2))
    print("df attributes = ", pm4py.get_event_attributes(df2))
    print("log org:resource values = ", pm4py.get_event_attribute_values(log2, "org:resource"))
    print("df org:resource values = ", pm4py.get_event_attribute_values(df2, "org:resource"))

    print("start_activities len(filt_log) = ", len(pm4py.filter_start_activities(log2, ["register request"])))
    print("start_activities len(filt_df) = ", len(pm4py.filter_start_activities(df2, ["register request"])))
    print("end_activities len(filt_log) = ", len(pm4py.filter_end_activities(log2, ["pay compensation"])))
    print("end_activities len(filt_df) = ", len(pm4py.filter_end_activities(df2, ["pay compensation"])))
    print("attributes org:resource len(filt_log) (cases) cases = ",
          len(pm4py.filter_event_attribute_values(log2, "org:resource", ["Ellen"], level="case")))
    print("attributes org:resource len(filt_log) (cases)  events = ",
          len(pm4py.filter_event_attribute_values(log2, "org:resource", ["Ellen"], level="event")))
    print("attributes org:resource len(filt_df) (events) cases = ",
          len(pm4py.filter_event_attribute_values(df2, "org:resource", ["Ellen"], level="case")))
    print("attributes org:resource len(filt_df) (events) events = ",
          len(pm4py.filter_event_attribute_values(df2, "org:resource", ["Ellen"], level="event")))
    print("attributes org:resource len(filt_df) (events) events notpositive = ",
          len(pm4py.filter_event_attribute_values(df2, "org:resource", ["Ellen"], level="event", retain=False)))

    print("rework df = ", pm4py.get_rework_cases_per_activity(df2))
    print("rework log = ", pm4py.get_rework_cases_per_activity(log2))
    print("cases overlap df = ", pm4py.get_case_overlap(df2))
    print("cases overlap log = ", pm4py.get_case_overlap(log2))
    print("cycle time df = ", pm4py.get_cycle_time(df2))
    print("cycle time log = ", pm4py.get_cycle_time(log2))
    pm4py.view_events_distribution_graph(df2, format="svg")
    pm4py.view_events_distribution_graph(log2, format="svg")

    print("variants log = ", pm4py.get_variants_as_tuples(log2))
    print("variants df = ", pm4py.get_variants_as_tuples(df2))
    print("variants filter log = ",
          len(pm4py.filter_variants(log2, [
              ("register request", "examine thoroughly", "check ticket", "decide", "reject request")])))
    print("variants filter df = ",
          len(pm4py.filter_variants(df2, [
              ("register request", "examine thoroughly", "check ticket", "decide", "reject request")])))

    print("paths filter log len = ",
          len(pm4py.filter_directly_follows_relation(log2, [("register request", "examine casually")])))
    print("paths filter dataframe len = ",
          len(pm4py.filter_directly_follows_relation(df2, [("register request", "examine casually")])))

    print("timeframe filter log events len = ",
          len(pm4py.filter_time_range(log2, "2011-01-01 00:00:00", "2011-02-01 00:00:00", mode="events")))
    print("timeframe filter log traces_contained len = ",
          len(pm4py.filter_time_range(log2, "2011-01-01 00:00:00", "2011-02-01 00:00:00", mode="traces_contained")))
    print("timeframe filter log traces_intersecting len = ",
          len(pm4py.filter_time_range(log2, "2011-01-01 00:00:00", "2011-02-01 00:00:00", mode="traces_intersecting")))
    print("timeframe filter df events len = ",
          len(pm4py.filter_time_range(df2, "2011-01-01 00:00:00", "2011-02-01 00:00:00", mode="events")))
    print("timeframe filter df traces_contained len = ",
          len(pm4py.filter_time_range(df2, "2011-01-01 00:00:00", "2011-02-01 00:00:00", mode="traces_contained")))
    print("timeframe filter df traces_intersecting len = ",
          len(pm4py.filter_time_range(df2, "2011-01-01 00:00:00", "2011-02-01 00:00:00", mode="traces_intersecting")))

    # remove the temporary files
    os.remove("ru1.xes")
    os.remove("ru_dfg.dfg")
    os.remove("ru_alpha.pnml")
    os.remove("ru_inductive.pnml")
    os.remove("ru_heuristics.pnml")
    os.remove("ru_inductive.ptml")
    os.remove("ru_alpha.png")
    os.remove("ru_inductive.png")
    os.remove("ru_heuristics.png")
    os.remove("ru_inductive_tree.png")
    os.remove("ru_heunet.png")
    os.remove("ru_dfg.png")

    os.remove("ev_time.png")
    os.remove("cd.png")
    os.remove("dotted_chart.png")
    os.remove("ps.png")

    wt_log = pm4py.discover_working_together_network(log2)
    wt_df = pm4py.discover_working_together_network(df2)
    print("log working together", wt_log)
    print("df working together", wt_df)
    print("log subcontracting", pm4py.discover_subcontracting_network(log2))
    print("df subcontracting", pm4py.discover_subcontracting_network(df2))
    print("log working together", pm4py.discover_working_together_network(log2))
    print("df working together", pm4py.discover_working_together_network(df2))
    print("log similar activities", pm4py.discover_activity_based_resource_similarity(log2))
    print("df similar activities", pm4py.discover_activity_based_resource_similarity(df2))
    print("log org roles", pm4py.discover_organizational_roles(log2))
    print("df org roles", pm4py.discover_organizational_roles(df2))
    pm4py.view_sna(wt_log)

    pm4py.save_vis_sna(wt_df, "ru_wt_df.png")
    os.remove("ru_wt_df.png")


if __name__ == "__main__":
    execute_script()

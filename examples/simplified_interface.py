import pm4py
import os


def execute_script():
    ENABLE_VISUALIZATION = False

    # reads a XES into an event log
    log1 = pm4py.read_xes("../tests/input_data/running-example.xes")

    # reads a CSV into a dataframe
    df = pm4py.read_csv("../tests/input_data/running-example.csv")
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
    # writes the df to a CSV file
    pm4py.write_csv(df, "ru1.csv")

    dfg = pm4py.discover_dfg(log1)
    petri_alpha = pm4py.discover_petri_net_alpha(log1)
    petri_inductive = pm4py.discover_petri_net_inductive(log1)
    petri_heuristics = pm4py.discover_petri_net_heuristics(log1)
    tree_inductive = pm4py.discover_tree_inductive(log1)
    heu_net = pm4py.discover_heuristics_net(log1)

    pm4py.write_dfg(dfg, "ru_dfg.dfg")
    pm4py.write_petri_net(petri_alpha, "ru_alpha.pnml")
    pm4py.write_petri_net(petri_inductive, "ru_inductive.pnml")
    pm4py.write_petri_net(petri_heuristics, "ru_heuristics.pnml")
    pm4py.write_process_tree(tree_inductive, "ru_inductive.ptml")

    dfg = pm4py.read_dfg("ru_dfg.dfg")
    petri_alpha = pm4py.read_petri_net("ru_alpha.pnml")
    petri_inductive = pm4py.read_petri_net("ru_inductive.pnml")
    petri_heuristics = pm4py.read_petri_net("ru_heuristics.pnml")
    tree_inductive = pm4py.read_process_tree("ru_inductive.ptml")

    pm4py.save_vis_petri_net(petri_alpha, "ru_alpha.png")
    pm4py.save_vis_petri_net(petri_inductive, "ru_inductive.png")
    pm4py.save_vis_petri_net(petri_heuristics, "ru_heuristics.png")
    pm4py.save_vis_process_tree(tree_inductive, "ru_inductive_tree.png")
    pm4py.save_vis_heuristics_net(heu_net, "ru_heunet.png")
    pm4py.save_vis_dfg(dfg, "ru_dfg.png")

    if ENABLE_VISUALIZATION:
        pm4py.view_petri_net(petri_alpha, format="svg")
        pm4py.view_petri_net(petri_inductive, format="svg")
        pm4py.view_petri_net(petri_heuristics, format="svg")
        pm4py.view_process_tree(tree_inductive, format="svg")
        pm4py.view_heuristics_net(heu_net, format="svg")
        pm4py.view_dfg(dfg, format="svg")

    aligned_traces = pm4py.conformance_alignments(log1, petri_inductive)
    replayed_traces = pm4py.conformance_tbr(log1, petri_inductive)

    fitness_tbr = pm4py.evaluate_fitness_tbr(log1, petri_inductive)
    print("fitness_tbr", fitness_tbr)
    fitness_align = pm4py.evaluate_fitness_alignments(log1, petri_inductive)
    print("fitness_align", fitness_align)
    precision_tbr = pm4py.evaluate_precision_tbr(log1, petri_inductive)
    print("precision_tbr", precision_tbr)
    precision_align = pm4py.evaluate_precision_alignments(log1, petri_inductive)
    print("precision_align", precision_align)

    print("log start activities = ", pm4py.get_start_activities(log2))
    print("df start activities = ", pm4py.get_start_activities(df2))
    print("log end activities = ", pm4py.get_end_activities(log2))
    print("df end activities = ", pm4py.get_end_activities(df2))
    print("log attributes = ", pm4py.get_attributes(log2))
    print("df attributes = ", pm4py.get_attributes(df2))
    print("log org:resource values = ", pm4py.get_attribute_values(log2, "org:resource"))
    print("df org:resource values = ", pm4py.get_attribute_values(df2, "org:resource"))

    print("start_activities len(filt_log) = ", len(pm4py.filter_start_activities(log2, ["register request"])))
    print("start_activities len(filt_df) = ", len(pm4py.filter_start_activities(df2, ["register request"])))
    print("end_activities len(filt_log) = ", len(pm4py.filter_end_activities(log2, ["pay compensation"])))
    print("end_activities len(filt_df) = ", len(pm4py.filter_end_activities(df2, ["pay compensation"])))
    print("attributes org:resource len(filt_log) (cases) cases = ",
          len(pm4py.filter_attribute_values(log2, "org:resource", ["Ellen"], how="cases")))
    print("attributes org:resource len(filt_log) (cases)  events = ",
          len(pm4py.filter_attribute_values(log2, "org:resource", ["Ellen"], how="events")))
    print("attributes org:resource len(filt_df) (events) cases = ",
          len(pm4py.filter_attribute_values(df2, "org:resource", ["Ellen"], how="cases")))
    print("attributes org:resource len(filt_df) (events) events = ",
          len(pm4py.filter_attribute_values(df2, "org:resource", ["Ellen"], how="events")))
    print("attributes org:resource len(filt_df) (events) events notpositive = ",
          len(pm4py.filter_attribute_values(df2, "org:resource", ["Ellen"], how="events", positive=False)))

    print("variants log = ", pm4py.get_variants(log2))
    print("variants df = ", pm4py.get_variants(df2))
    print("variants filter log = ",
          len(pm4py.filter_variants(log2, ["register request,examine thoroughly,check ticket,decide,reject request"])))
    print("variants filter df = ",
          len(pm4py.filter_variants(df2, ["register request,examine thoroughly,check ticket,decide,reject request"])))
    print("variants filter percentage = ", len(pm4py.filter_variants_percentage(log2, percentage=0.8)))

    # remove the temporary files
    os.remove("ru1.xes")
    os.remove("ru1.csv")
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


if __name__ == "__main__":
    execute_script()

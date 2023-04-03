import pm4py


def execute_script():
    log = pm4py.read_xes("../tests/input_data/roadtraffic100traces.xes")
    ocel = pm4py.read_ocel("../tests/input_data/ocel/example_log.jsonocel")

    print(pm4py.openai.describe_process(log))

    print(pm4py.openai.describe_activity(log, "Send for Credit Collection"))

    print(pm4py.openai.describe_path(log, ("Send for Credit Collection", "Payment")))

    print(pm4py.openai.describe_variant(log, ("Create Fine", "Send Fine", "Payment", "Send for Credit Collection")))

    print(pm4py.openai.suggest_improvements(log))

    print(pm4py.openai.root_cause_analysis(log))

    print(pm4py.openai.code_for_log_generation("Purchase-to-Pay"))

    log = pm4py.insert_artificial_start_end(log)
    cases_tpa_100 = log[log["totalPaymentAmount"] > 100]["case:concept:name"].unique()
    log1 = log[~log["case:concept:name"].isin(cases_tpa_100)]
    log2 = log[log["case:concept:name"].isin(cases_tpa_100)]

    print(pm4py.openai.compare_logs(log1, log2))

    print(pm4py.openai.abstract_dfg(log))

    print(pm4py.openai.abstract_variants(log))

    print(pm4py.openai.abstract_ocel(ocel))

    print(pm4py.openai.anomaly_detection(log))

    print(pm4py.openai.suggest_clusters(log))

    print(pm4py.openai.conformance_checking(log, "all traces should contain a single payment"))


if __name__ == "__main__":
    execute_script()

import pm4py


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes")
    fea_df = pm4py.extract_features_dataframe(log, include_case_id=True)
    # sets the case ID as index for the dataframe, so a row for a specific case
    # can be retrieved
    fea_df = fea_df.set_index("case:concept:name")
    # identifies the features for the case with identifier "case-10017"
    features_per_case = fea_df.loc["case-10017"].to_dict()
    print(features_per_case)


if __name__ == "__main__":
    execute_script()

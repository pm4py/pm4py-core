import pm4py
import os
import duckdb


def execute_script():
    """
    Scripts to check the query provided (in the script 01_1_...) for the "protected"
    group against the ground truth (that for the logs included in pm4py is reported in the log)
    and measure the quality of the classification.
    """
    dataframe = pm4py.read_xes("../../tests/input_data/fairness/renting_log_high.xes.gz")
    protected_attr = [x for x in dataframe.columns if "protected" in x][0]

    sql_query = """
SELECT * FROM dataframe 
WHERE "case:citizen" = 'False' 
OR "case:gender" = 'True' 
OR "case:german speaking" = 'False' 
OR "case:married" = 'False';
    """
    dataframe_pos = duckdb.sql(sql_query).to_df()
    cases_pos = dataframe_pos["case:concept:name"].unique()
    dataframe_neg = dataframe[~dataframe["case:concept:name"].isin(cases_pos)]

    dataframe_pos = dataframe_pos.groupby("case:concept:name").first()
    dataframe_neg = dataframe_neg.groupby("case:concept:name").last()

    tp = len(dataframe_pos[dataframe_pos[protected_attr] == True])
    fp = len(dataframe_pos[dataframe_pos[protected_attr] == False])
    print("true positives", tp)
    print("false positives", fp)
    fn = len(dataframe_neg[dataframe_neg[protected_attr] == True])
    tn = len(dataframe_neg[dataframe_neg[protected_attr] == False])
    print("false negatives", fn)
    print("true negatives", tn)


if __name__ == "__main__":
    execute_script()

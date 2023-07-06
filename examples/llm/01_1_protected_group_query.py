import pm4py
import os
import duckdb


def execute_script():
    log_path = os.path.join(r"C:\Users\berti\fairness xes logs", "hospital_log_high.xes.gz")
    dataframe = pm4py.read_xes(log_path)
    sql_query = """
SELECT *
FROM dataframe
WHERE "case:citizen" = 'False'
OR "case:german speaking" = 'False'
OR "case:private_insurance" = 'False'
OR "case:underlying_condition" = 'True';
    """
    dataframe_pos = duckdb.sql(sql_query).to_df()
    cases_pos = dataframe_pos["case:concept:name"].unique()
    dataframe_neg = dataframe[~dataframe["case:concept:name"].isin(cases_pos)]

    dataframe_pos = dataframe_pos.groupby("case:concept:name").first()
    dataframe_neg = dataframe_neg.groupby("case:concept:name").last()

    tp = len(dataframe_pos[dataframe_pos["protected"] == True])
    fp = len(dataframe_pos[dataframe_pos["protected"] == False])
    print("true positives", tp)
    print("false positives", fp)
    fn = len(dataframe_neg[dataframe_neg["protected"] == True])
    tn = len(dataframe_neg[dataframe_neg["protected"] == False])
    print("false negatives", fn)
    print("true negatives", tn)


if __name__ == "__main__":
    execute_script()

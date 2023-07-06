import pm4py
import os
import duckdb


def execute_script():
    log_path = os.path.join(r"C:\Users\berti\fairness xes logs", "hospital_log_high.xes.gz")
    dataframe = pm4py.read_xes(log_path)
    protected_attr = [x for x in dataframe.columns if "protected" in x][0]

    sql_query = """
    WITH process_variants AS (
        SELECT *, 
               STRING_AGG("concept:name", ' -> ') OVER(PARTITION BY "case:concept:name" ORDER BY "time:timestamp") AS variant,
               (MAX(EPOCH("time:timestamp")) OVER(PARTITION BY "case:concept:name") - MIN(EPOCH("time:timestamp")) OVER(PARTITION BY "case:concept:name")) AS duration
        FROM dataframe
    )
    SELECT *
    FROM process_variants
    WHERE variant NOT IN (
        'Register at ER -> Examination -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at FD -> Examination -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at FD -> Expert Examination -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at ER -> Expert Examination -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at FD -> Examination -> Thorough Examination -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at ER -> Examination -> Thorough Examination -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at FD -> Expert Examination -> Thorough Examination -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at ER -> Expert Examination -> Thorough Examination -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at ER -> Examination -> Diagnosis -> Treatment -> Treatment unsuccessful -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at FD -> Examination -> Diagnosis -> Treatment -> Treatment unsuccessful -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at ER -> Expert Examination -> Thorough Examination -> Diagnosis -> Treatment -> Treatment unsuccessful -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at FD -> Expert Examination -> Thorough Examination -> Diagnosis -> Treatment -> Treatment unsuccessful -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at ER -> Expert Examination -> Diagnosis -> Treatment -> Treatment unsuccessful -> Diagnosis -> Treatment -> Treatment successful -> Discharge',
        'Register at FD -> Expert Examination -> Diagnosis -> Treatment -> Treatment unsuccessful -> Diagnosis -> Treatment -> Treatment successful -> Discharge'
    )
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

import pm4py
import os
import duckdb


def execute_script():
    """
    Measures the quality of the SQL query provided in 02_...
    to isolate the procedural behavior leading to discrimination,
    and assess the quality of the classification against the ground truth written in the log.
    """
    dataframe = pm4py.read_xes("../../tests/input_data/fairness/renting_log_high.xes.gz")
    protected_attr = [x for x in dataframe.columns if "protected" in x][0]

    sql_query = """
WITH cases AS (
    SELECT 
        "case:concept:name", 
        STRING_AGG("concept:name", ' -> ') OVER (PARTITION BY "case:concept:name" ORDER BY "time:timestamp") AS variant
    FROM 
        dataframe 
), 
filtered_cases AS (
    SELECT 
        "case:concept:name"
    FROM 
        cases 
    WHERE variant IN (
    'Request Appointment -> Set Appointment -> Hand In Credit Appliaction -> Verify Borrowers Information -> Submit File to Underwriter -> Loan Denied',
    'Request Appointment -> Set Appointment -> Hand In Credit Appliaction -> Verify Borrowers Information -> Application Rejected',
    'Request Appointment -> Appointment Denied',
    'Request Appointment -> Set Appointment -> Hand In Credit Appliaction -> Verify Borrowers Information -> Request Co-Signer On Loan -> Submit File to Underwriter -> Loan Denied',
    'Request Appointment -> Set Appointment -> Hand In Credit Appliaction -> Verify Borrowers Information -> Make Visit to Assess Colatteral -> Submit File to Underwriter -> Loan Denied',
    'Request Appointment -> Set Appointment -> Hand In Credit Appliaction -> Verify Borrowers Information -> Make Visit to Assess Colatteral -> Submit File to Underwriter -> Sign Loan Agreement'
)
    GROUP BY
        "case:concept:name"
)
SELECT 
    df.*, 
    cases.variant
FROM 
    dataframe AS df
JOIN 
    filtered_cases ON df."case:concept:name" = filtered_cases."case:concept:name"
JOIN
    cases ON df."case:concept:name" = cases."case:concept:name"
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

import os
import time
import traceback

log_name = "receipt.parquet"
# legacy support
allowed_columns = ["caseAAAconceptAAAname", "conceptAAAname"]

def execute_script():
    try:
        from pm4py.objects.log.importer.parquet import factory as parquet_importer
        from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics

        log_path = os.path.join("..", "tests", "input_data", log_name)
        time1 = time.time()
        dataframe = parquet_importer.apply(log_path, parameters={"columns": allowed_columns})
        time2 = time.time()
        print(dataframe.columns)
        print("time interlapsed importing "+log_name+" on columns "+str(allowed_columns)+": ",(time2-time1))
        dfg1 = df_statistics.get_dfg_graph(dataframe, sort_timestamp_along_case_id=False)
        time3 = time.time()
        print("time interlapsed calculating the DFG on columns "+str(allowed_columns)+" : ",(time3-time2))
        del dataframe
        time4 = time.time()
        dataframe = parquet_importer.apply(log_path)
        print(dataframe.columns)
        time5 = time.time()
        print("time interlapsed importing "+log_name+" (all columns): ",(time5-time4))
        dfg2 = df_statistics.get_dfg_graph(dataframe, sort_timestamp_along_case_id=False)
        time6 = time.time()
        print("time interlapsed calculating the DFG on all columns : ",(time6-time5))
    except:
        traceback.print_exc()


if __name__ == "__main__":
    execute_script()

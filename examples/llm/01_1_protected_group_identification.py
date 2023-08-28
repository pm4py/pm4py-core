import pm4py
import os


def execute_script():
    """
    Prompt asking to the LLM to generate a SQL query that, given the attributes of the event log,
    identifies the cases with higher risk of discrimination ("protected" group).
    """
    dataframe = pm4py.read_xes("../../tests/input_data/fairness/renting_log_high.xes.gz")
    dataframe = dataframe[[x for x in dataframe.columns if 'protected' not in x]]
    print(dataframe)
    print(dataframe.columns)
    prompt = "Given an event log describing a process with the following directly-follows graph:\n\n"
    prompt += pm4py.llm.abstract_dfg(dataframe, max_len=5000, response_header=False)
    prompt += "\n\nand the following attributes:\n\n"
    prompt += pm4py.llm.abstract_log_attributes(dataframe, max_len=5000)
    prompt += "\n\nCould you make an hypothesis and provide me a DuckDB SQL query that I can execute to filter the dataframe on the cases in which unfairness is likely to happen? It can be an OR query (several different conditions could signal unfairness) The dataframe is called 'dataframe'. Please only a single query. The single query should only look at the case attributes, not the activities in a case. Quote the names of the attributes with a \" at start and at the end."
    print(prompt)


if __name__ == "__main__":
    execute_script()

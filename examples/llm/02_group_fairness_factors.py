import pm4py
import os


def execute_script():
    """
    Script that, given the process variants of the "protected" and "non-protected" groups,
    generates a (first) prompt asking to the LLM which are the procedural differences between the two groups.
    The second prompt works on the output of the first prompt, and generates a SQL query isolating the
    paths or the process variants that lead to discrimination.
    """
    dataframe = pm4py.read_xes("../../tests/input_data/fairness/renting_log_high.xes.gz")
    protected_attr = [x for x in dataframe.columns if "protected" in x][0]
    dataframe_prot = dataframe[dataframe[protected_attr] == True]
    dataframe_unprot = dataframe[dataframe[protected_attr] == False]
    prompt = "I want to identify the unfair differences between the treatment of the 'protected' group (first) and the 'unprotected' group (second). I report the process variants. Each process variant is also reported with its execution time."
    prompt += "\n\nProcess variants of the protected group:"
    prompt += pm4py.llm.abstract_variants(dataframe_prot, max_len=5000)
    prompt += "\n\nProcess variants of the unprotected group:"
    prompt += pm4py.llm.abstract_variants(dataframe_unprot, max_len=5000)
    prompt += "\n\nwhich are the main differences? use your domain knowledge."
    print(prompt)
    input()
    prompt = "Perfect. Now please provide me a single DuckDB SQL query to filter the dataframe to such variants that are critical for fairness. More in detail, the data is stored in a Pandas dataframe where each row is an event having the provided attributes (so there are no separate table containing the variant). Please consider the following information: the case identifier is called 'case:concept:name', the activity is stored inside the attribute 'concept:name', the timestamp is stored inside the attribute 'time:timestamp', the resource is stored inside the attribute 'org:resource', there is not a variant column but that can be obtained as concatenation of the activities of a case, there is not a duration column but that can be obtained as difference between the timestamp of the first and the last event. Also, the dataframe is called 'dataframe'. You should use the EPOCH function of DuckDB to get the timestamp from the date. Note that I want the original dataframe with its rows and columns back (so add the variant column on the original dataframe and filter on that). Please filter on a comprehensive list of unfair variants, use several messages if necessary."
    print(prompt)


if __name__ == "__main__":
    execute_script()

import pm4py


def execute_script():
    """
    Generates some hypothesis for the analysis of an event log starting
    from the process variants and log attributes abstraction of the event log.
    The hypothesis shall come with a DuckDB SQL query that can be verified against the dataframe
    """
    log = pm4py.read_xes("../../tests/input_data/roadtraffic100traces.xes")
    prompt = []
    prompt.append("\n\nIf I have the following process variants:\n")
    prompt.append(pm4py.llm.abstract_variants(log, max_len=3000, response_header=False))
    prompt.append("\n\nand attributes in the log:\n")
    prompt.append(pm4py.llm.abstract_log_attributes(log, max_len=3000))
    prompt.append("\n\n")
    prompt.append("can you formulate some hypothesis on the given process?\n")
    prompt.append("please also formulate for every hypothesis a SQL query.\n")
    prompt.append("\n\n")
    prompt.append("Can you provide me a DuckDB SQL query.\n")
    prompt.append("You should use the EPOCH function of DuckDB to get the timestamp from the date.\n")
    prompt.append("The data is stored in a Pandas dataframe where each row is an event having the provided attributes (so there are no separate table containing the variant).\n")
    prompt.append('The dataframe is called "dataframe".\n')
    prompt.append('Please consider the following information: the case identifier is called "case:concept:name", the activity is stored inside the attribute "concept:name", the timestamp is stored inside the attribute "time:timestamp", the resource is stored inside the attribute "org:resource".\n')
    prompt.append('There is not a variant column but that can be obtained as concatenation of the activities of a case.\n')
    prompt.append('There is not a duration column but that can be obtained as difference between the timestamp of the first and the last event.\n')
    prompt.append("\n\n")
    prompt = "".join(prompt)
    print(prompt)


if __name__ == "__main__":
    execute_script()

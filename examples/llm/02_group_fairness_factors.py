import pm4py
import os


def execute_script():
    log_path = os.path.join(r"C:\Users\berti\fairness xes logs", "hospital_log_high.xes.gz")
    dataframe = pm4py.read_xes(log_path)
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


if __name__ == "__main__":
    execute_script()

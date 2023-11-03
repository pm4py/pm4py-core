import pm4py
from pm4py.algo.label_splitting import algorithm as label_splitter


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes")
    log = log[["case:concept:name", "concept:name", "time:timestamp"]]

    # relabeling with the default options
    rlog1 = label_splitter.apply(log, variant=label_splitter.Variants.CONTEXTUAL)
    print(rlog1)

    # relabeling with a single activity allowed in the prefix and suffix,
    # plus the relabeling only applies to a given activity
    rlog2 = label_splitter.apply(log, variant=label_splitter.Variants.CONTEXTUAL,
                                 parameters={"prefix_length": 1, "suffix_length": 1,
                                             "target_activities": ["Confirmation of receipt"]})
    print(rlog2)


if __name__ == "__main__":
    execute_script()

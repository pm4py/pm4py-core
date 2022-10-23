import os
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.organizational_mining.roles import algorithm as roles_algorithm


def execute_script():
    # import the log
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"), variant="nonstandard")

    roles = roles_algorithm.apply(log)

    # print the results (grouped activities) on the screen
    print([x.activities for x in roles])


if __name__ == "__main__":
    execute_script()

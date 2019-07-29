import os
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.enhancement.roles import factory as roles_factory


def execute_script():
    # import the log
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"), variant="nonstandard")

    # execute the roles detection factory
    roles = roles_factory.apply(log)

    # print the results (grouped activities) on the screen
    print([x[0] for x in roles])


if __name__ == "__main__":
    execute_script()

from pm4py.algo.other.decisiontree.applications import decision_mining_given_activities
from pm4py.objects.log.importer.xes import factory as xes_importer


def execute_script():
    log = xes_importer.apply("C:\\running-example.xes")
    rules = decision_mining_given_activities.get_decision_mining_rules_given_activities(log, ["pay compensation",
                                                                                              "reject request"])
    print("Decision rules = ")
    print(rules)


if __name__ == "__main__":
    execute_script()

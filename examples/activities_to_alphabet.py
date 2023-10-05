import pm4py
from pm4py.objects.log.util import activities_to_alphabet
from pm4py.util import constants


def execute_script():
    dataframe = pm4py.read_xes("../tests/input_data/running-example.xes", return_legacy_log_object=False)
    renamed_dataframe = activities_to_alphabet.apply(dataframe, parameters={constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "concept:name"})
    print(renamed_dataframe)


if __name__ == "__main__":
    execute_script()

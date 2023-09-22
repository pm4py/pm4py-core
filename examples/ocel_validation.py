from pm4py.objects.ocel.validation import jsonocel, xmlocel
import os
import importlib.util


def execute_script():
    if importlib.util.find_spec("jsonschema"):
        # validate a JSONOCEL file against the corresponding schema
        validation_result = jsonocel.apply(os.path.join("..", "tests", "input_data", "ocel", "example_log.jsonocel"), os.path.join("..", "tests", "input_data", "ocel", "validation", "schema.json"))
        print(validation_result)
        # validate an XMLOCEL file against the corresponding schema
        validation_result = xmlocel.apply(os.path.join("..", "tests", "input_data", "ocel", "example_log.xmlocel"), os.path.join("..", "tests", "input_data", "ocel", "validation", "schema.xml"))
        print(validation_result)


if __name__ == "__main__":
    execute_script()

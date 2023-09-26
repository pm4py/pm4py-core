import importlib.util


def apply(input_path, validation_path, parameters=None):
    if not importlib.util.find_spec("jsonschema"):
        raise Exception("please install jsonschema in order to validate a JSONOCEL file.")

    import json
    import jsonschema
    from jsonschema import validate

    if parameters is None:
        parameters = {}

    file_content = json.load(open(input_path, "rb"))
    schema_content = json.load(open(validation_path, "rb"))
    try:
        validate(instance=file_content, schema=schema_content)
        return True
    except jsonschema.exceptions.ValidationError as err:
        return False

from pm4py.objects.ocel.validation import xmlocel


def execute_script():
    file_path = "../tests/input_data/ocel/ocel20_example.xmlocel"
    validation_path = "../tests/input_data/ocel/ocel2-validation.xsd"

    is_valid = xmlocel.apply(file_path, validation_path)

    print(is_valid)


if __name__ == "__main__":
    execute_script()

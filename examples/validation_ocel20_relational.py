from pm4py.objects.ocel.validation import ocel20_rel_validation


def execute_script():
    file_path = "../tests/input_data/ocel/ocel20_example.sqlite"

    satisfied, unsatisfied = ocel20_rel_validation.apply(file_path)

    print("satisfied", satisfied)
    print("unsatisfied", unsatisfied)


if __name__ == "__main__":
    execute_script()

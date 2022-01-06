import pm4py
from pm4py.objects.process_tree.obj import ProcessTree, Operator


def execute_script():
    root = ProcessTree(operator=Operator.SEQUENCE)

    choice = ProcessTree(operator=Operator.XOR, parent=root)
    parallel = ProcessTree(operator=Operator.PARALLEL, parent=root)

    root.children.append(choice)
    root.children.append(parallel)

    leaf_A = ProcessTree(label="A", parent=choice)
    leaf_B = ProcessTree(label="B", parent=choice)
    leaf_C = ProcessTree(label="C", parent=choice)

    choice.children.append(leaf_A)
    choice.children.append(leaf_B)
    choice.children.append(leaf_C)

    leaf_D = ProcessTree(label="D", parent=parallel)
    leaf_E = ProcessTree(label="E", parent=parallel)
    leaf_F = ProcessTree(label="F", parent=parallel)

    parallel.children.append(leaf_D)
    parallel.children.append(leaf_E)
    parallel.children.append(leaf_F)

    pm4py.view_process_tree(root, format="svg")

    # remove leaf_C from choice
    choice.children.remove(leaf_C)

    # remove the leaf with label "E" from parallel
    parallel.children.remove(
        [parallel.children[i] for i in range(len(parallel.children)) if parallel.children[i].label == "E"][0])

    pm4py.view_process_tree(root, format="svg")


if __name__ == "__main__":
    execute_script()

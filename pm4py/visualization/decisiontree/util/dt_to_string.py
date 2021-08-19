from sklearn import tree
from typing import Dict, Tuple, Set, List


def apply(clf: tree.DecisionTreeClassifier, columns: List[str]) -> Tuple[Dict[str, str], Dict[str, Set[str]]]:
    """
    Translates a decision tree object into a dictionary
    associating a set of conditions for each target class

    Parameters
    ----------------
    clf
        Decision tree classifier
    columns
        Columns

    Returns
    ----------------
    dict_classes
        Dictionary associating a set of conditions for each target class
    """
    tree_string = tree.export_text(clf).split("\n")
    levels = {}
    target_classes = {}
    variables = {}
    i = 0
    while i < len(tree_string):
        if "---" in tree_string[i]:
            level = len(tree_string[i].split("|")) - 2
            this_part = tree_string[i].split("--- ")[1]
            this_part_idx_space = this_part.index(" ")
            this_part_0 = this_part[:this_part_idx_space]
            this_part_1 = this_part[this_part_idx_space+1:]
            if "class" in this_part:
                all_levels = "(" + " && ".join([levels[i] for i in range(level)]) + ")"
                target_class = this_part.split(": ")[-1]
                if target_class not in target_classes:
                    target_classes[target_class] = []
                target_classes[target_class].append(all_levels)
                if target_class not in variables:
                    variables[target_class] = set()
                for j in range(level):
                    variables[target_class].add(levels[j].split(" ")[0])
            else:
                levels[level] = columns[int(this_part_0.split("_")[1])] + " " + this_part_1
        i = i + 1
    for cl in target_classes:
        target_classes[cl] = " || ".join(target_classes[cl])
    return target_classes, variables

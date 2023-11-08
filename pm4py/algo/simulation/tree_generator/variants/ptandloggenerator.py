'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from pm4py.objects.process_tree import obj
from pm4py.objects.process_tree import obj as pt_operator
from scipy.stats import triang as triangular
import string
from enum import Enum
from itertools import accumulate as _accumulate, repeat as _repeat
from bisect import bisect as _bisect
import random
from typing import Optional, Dict, Any, Union
from string import ascii_lowercase
import itertools


def choices(population, weights=None, *, cum_weights=None, k=1):
    """Return a k sized list of population elements chosen with replacement.
    If the relative weights or cumulative weights are not specified,
    the selections are made with equal probability.
    """
    n = len(population)
    if cum_weights is None:
        if weights is None:
            _int = int
            n += 0.0    # convert to float for a small speed improvement
            return [population[_int(random.random() * n)] for i in _repeat(None, k)]
        cum_weights = list(_accumulate(weights))
    elif weights is not None:
        raise TypeError('Cannot specify both weights and cumulative weights')
    if len(cum_weights) != n:
        raise ValueError('The number of weights does not match the population')
    bisect = _bisect
    total = cum_weights[-1] + 0.0   # convert to float
    hi = n - 1
    return [population[bisect(cum_weights, random.random() * total, 0, hi)]
            for i in _repeat(None, k)]


class Parameters(Enum):
    SEQUENCE = "sequence"
    CHOICE = "choice"
    PARALLEL = "parallel"
    LOOP = "loop"
    OR = "or"
    MODE = "mode"
    MIN = "min"
    MAX = "max"
    SILENT = "silent"
    DUPLICATE = "duplicate"
    NO_MODELS = "no_models"


def apply(parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> obj.ProcessTree:
    """
    Generate a process tree using the PTAndLogGenerator approach
    (see the paper PTandLogGenerator: A Generator for Artificial Event Data)

    Parameters
    --------------
    parameters
        Parameters of the algorithm, according to the paper:
        - Parameters.MODE: most frequent number of visible activities
        - Parameters.MIN: minimum number of visible activities
        - Parameters.MAX: maximum number of visible activities
        - Parameters.SEQUENCE: probability to add a sequence operator to tree
        - Parameters.CHOICE: probability to add a choice operator to tree
        - Parameters.PARALLEL: probability to add a parallel operator to tree
        - Parameters.LOOP: probability to add a loop operator to tree
        - Parameters.OR: probability to add an or operator to tree
        - Parameters.SILENT: probability to add silent activity to a choice or loop operator
        - Parameters.DUPLICATE: probability to duplicate an activity label
        - Parameters.NO_MODELS: number of trees to generate from model population
    """
    if parameters is None:
        parameters = {}

    if not "mode" in parameters:
        parameters["mode"] = 20
    if not "min" in parameters:
        parameters["min"] = 10
    if not "max" in parameters:
        parameters["max"] = 30
    if not "sequence" in parameters:
        parameters["sequence"] = 0.25
    if not "choice" in parameters:
        parameters["choice"] = 0.25
    if not "parallel" in parameters:
        parameters["parallel"] = 0.25
    if not "loop" in parameters:
        parameters["loop"] = 0.25
    if not "or" in parameters:
        parameters["or"] = 0.0
    if not "silent" in parameters:
        parameters["silent"] = 0.2
    if not "duplicate" in parameters:
        parameters["duplicate"] = 0
    if not "no_models" in parameters:
        parameters["no_models"] = 1

    no_models = parameters["no_models"]

    if no_models == 1:
        return GeneratedTree(parameters).generate()
    else:
        # if the generation of an higher number of models is required,
        # proceed to the generation of these and return a list of
        # process trees.
        ret = []
        for i in range(no_models):
            ret.append(GeneratedTree(parameters).generate())
        return ret


def assign_operator(operator):
    if operator == "choice":
        return pt_operator.Operator.XOR
    elif operator == "sequence":
        return pt_operator.Operator.SEQUENCE
    elif operator == "parallel":
        return pt_operator.Operator.PARALLEL
    elif operator == "or":
        return pt_operator.Operator.OR
    elif operator == "loop":
        return pt_operator.Operator.LOOP
    else:
        return None


class GeneratedTree(object):
    # are later used as labels
    alphabet = string.ascii_lowercase

    def calculate_activity_distribution(self, mode, min, max):
        """
        Here, the triangular function is used, since the parameters for this function are given in the paramterfile.
        However, this approach can be applied on other distribution functions as well.
        :param mode: Mode of the distribution
        :param min: Smallest number
        :param max: Highest number
        :return: Distribution object
        """
        # manage the case where min = mode = max
        c = (mode - min + 10**-12) / (max - min + 10**-6)
        ret = triangular(c, loc=min, scale=max - min)
        return ret

    def draw_random_number_from_distribution(self):
        return self.activity_distribution.rvs(1)[0]

    def select_operator(self):
        # add root operator, if probabilities are high enough
        # ordering of operator computation is sequence, choice, parallel, loop, or
        operator = choices(["sequence", "choice", "parallel", "loop", "or"],
                                  [self.parameters["sequence"], self.parameters["choice"], self.parameters["parallel"],
                                   self.parameters["loop"], self.parameters["or"]])
        return operator[0]

    def get_next_activity(self):
        result = self.iter.__next__()
        return result


    def add_duplicates(self):
        """
        Replaces some leaves  to add duplicated labels. Depends on parameter.
        :return:
        """
        duplication_allowed = False
        leaves = self.tree._get_leaves()
        for leaf in leaves:
            if leaf._parent != self.tree._get_root():
                duplication_allowed = True
                break
        # if there is at least a depth of two
        if duplication_allowed:
            # list that contains the leaves with a label unequal to tau
            leaves_with_label = []
            for leaf in leaves:
                if leaf.label is not None:
                    leaves_with_label.append(leaf)
            # generate random list of duplicates
            duplicates = []
            for leaf in leaves:
                if random.random() < self.parameters["duplicate"]:
                    duplicates.append(leaf)
            if len(duplicates) > 0:
                # select potential leaves to replace them by duplicates
                possible_replacements = []
                for leaf in leaves:
                    if leaf not in duplicates:
                        possible_replacements.append(leaf)
            for leaf in duplicates:
                i = 0
                siblings = []
                # determine sibling nodes (same parent)
                p = leaf._parent
                for child in p._children:
                    if child != leaf:
                        siblings.append(child)
                # TODO Skaling? Original: 30times, my idea : percentage of duplicates * len(leaves)
                while i < self.parameters["duplicate"] * len(leaves):
                    replacement = random.choice(possible_replacements)
                    if replacement not in siblings:
                        replacement._label = leaf._label
                        break

    def add_node(self):
        leaves = self.tree._get_leaves()
        if self.tree.operator is None:
            leaves.append(self.tree)
        visible_leaves = [x for x in leaves if x.label is not None]
        operator = self.select_operator()
        op_map = {"parallel": obj.Operator.PARALLEL, "sequence": obj.Operator.SEQUENCE, "choice": obj.Operator.XOR, "loop": obj.Operator.LOOP, "or": obj.Operator.OR}
        mapped_operator = op_map[operator]
        order = random.randrange(0, 2)
        chosen_leaf = random.choice(leaves)
        added_count = 0
        label1 = chosen_leaf.label
        if chosen_leaf.label is None:
            added_count = added_count + 1
            label1 = self.get_next_activity()
        label2 = None
        if chosen_leaf.parent is None:
            self.tree = obj.ProcessTree(operator=mapped_operator)
            chosen_leaf = self.tree
        else:
            parent = chosen_leaf.parent
            del parent.children[parent.children.index(chosen_leaf)]
            chosen_leaf = obj.ProcessTree(operator=mapped_operator, parent=parent)
            parent.children.append(chosen_leaf)
        r = random.random()
        if self.total_activities - len(visible_leaves) > added_count and not r < self.parameters["silent"]:
            label2 = self.get_next_activity()
        node1 = obj.ProcessTree(label=label1, parent=chosen_leaf)
        node2 = obj.ProcessTree(label=label2, parent=chosen_leaf)
        if order == 0:
            chosen_leaf.children.append(node1)
            chosen_leaf.children.append(node2)
        elif order == 1:
            chosen_leaf.children.append(node2)
            chosen_leaf.children.append(node1)

    def iter_all_strings(self):
        for size in itertools.count(1):
            for s in itertools.product(ascii_lowercase, repeat=size):
                yield "".join(s)

    def create_process_tree(self):
        self.iter = self.iter_all_strings()
        self.tree = obj.ProcessTree()
        visible_leaves = [x for x in self.tree._get_leaves() if x.label is not None]
        while len(visible_leaves) < self.total_activities:
            self.add_node()
            visible_leaves = [x for x in self.tree._get_leaves() if x.label is not None]

    def __init__(self, parameters):
        self.parameters = {}
        for param in parameters:
            p = param if type(param) is str else param.value
            self.parameters[p] = parameters[param]
        # rescale probabilities of operators if the sum is not equal to one
        if self.parameters["sequence"] + self.parameters["choice"] + self.parameters["parallel"] + self.parameters[
            "loop"] + self.parameters["or"] != 1:
            sum_of_operators = self.parameters["sequence"] + self.parameters["choice"] + self.parameters["parallel"] + \
                               self.parameters["loop"] + self.parameters["or"]
            self.parameters["sequence"] = self.parameters["sequence"] / sum_of_operators
            self.parameters["choice"] = self.parameters["choice"] / sum_of_operators
            self.parameters["parallel"] = self.parameters["parallel"] / sum_of_operators
            self.parameters["or"] = self.parameters["or"] / sum_of_operators
            self.parameters["loop"] = self.parameters["loop"] / sum_of_operators
        # First step: Compute acivity distribution
        # Since mode, min and max are given, the triangle distribution is chosen
        self.activity_distribution = self.calculate_activity_distribution(self.parameters["mode"],
                                                                          self.parameters["min"],
                                                                          self.parameters["max"])
        # Number of total activities represented in the tree. Also, tau is counted as an activity.
        self.total_activities = int(round(self.draw_random_number_from_distribution()))


    def generate(self):
        # Create a process tree based on the given probabilities
        self.create_process_tree()
        # add duplicates
        self.add_duplicates()

        return self.tree

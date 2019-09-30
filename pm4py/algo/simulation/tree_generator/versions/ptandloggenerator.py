from pm4py.objects.process_tree import process_tree
from pm4py.objects.process_tree import pt_operator
from scipy.stats import triang as triangular
import string
import math
import itertools
import random
import copy

def apply(parameters=None):
    """
    Generate a process tree using the PTAndLogGenerator approach
    (see the paper PTandLogGenerator: A Generator for Artificial Event Data)

    Parameters
    --------------
    parameters
        Parameters of the algorithm, according to the paper:
        - mode: most frequent number of visible activities
        - min: minimum number of visible activities
        - max: maximum number of visible activities
        - sequence: probability to add a sequence operator to tree
        - choice: probability to add a choice operator to tree
        - parallel: probability to add a parallel operator to tree
        - loop: probability to add a loop operator to tree
        - or: probability to add an or operator to tree
        - silent: probability to add silent activity to a choice or loop operator
        - duplicate: probability to duplicate an activity label
        - lt_dependency: probability to add a random dependency to the tree
        - infrequent: probability to make a choice have infrequent paths
        - no_models: number of trees to generate from model population
        - unfold: whether or not to unfold loops in order to include choices underneath in dependencies: 0=False, 1=True
            if lt_dependency <= 0: this should always be 0 (False)
            if lt_dependency > 0: this can be 1 or 0 (True or False)
        - max_repeat: maximum number of repetitions of a loop (only used when unfolding is True)
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
    if not "lt_depencency" in parameters:
        parameters["lt_depencency"] = 0.0
    if not "infrequent" in parameters:
        parameters["infrequent"] = 0.5
    if not "no_models" in parameters:
        parameters["no_models"] = 10
    if not "unfold" in parameters:
        parameters["unfold"] = 10
    if not "max_repeat" in parameters:
        parameters["max_repeat"] = 10

    return GeneratedTree(parameters).generate()

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
        c = (mode - min) / (max - min)
        return triangular(c, loc=min, scale=max - min)

    def draw_random_number_from_distribution(self):
        return self.activity_distribution.rvs(1)[0]

    def select_operator(self):
        # add root operator, if probabilities are high enough
        # ordering of operator computation is sequence, choice, parallel, loop, or
        operator = random.choices(["sequence", "choice", "parallel", "loop", "or"],
                                  [self.parameters["sequence"], self.parameters["choice"], self.parameters["parallel"],
                                   self.parameters["loop"], self.parameters["or"]])
        return operator[0]

    def get_next_activity(self, activity):
        result = self.set_activity_labels[self.set_activity_labels.index(activity) + 1]
        return result

    def assign_root_opeartor(self):
        activity = "a"
        # is a silent activity chosen
        silent_activity = False
        if random.random() < self.parameters["silent"]:
            silent_activity = True
        root = self.tree._get_root()
        operator = self.select_operator()
        root.operator = assign_operator(operator)
        # if operator is loop, we use a special structure, otherwise 2
        if operator == "loop":
            root.operator = pt_operator.Operator.SEQUENCE
            root_loop = process_tree.ProcessTree(operator=pt_operator.Operator.LOOP)
            root_loop.parent = root
            root._children.append(copy.copy(root_loop))
            new_node = process_tree.ProcessTree(label=activity)
            new_node.parent = root_loop
            root_loop._children.append(copy.copy(new_node))
            activity = self.get_next_activity(activity)
            if silent_activity:
                new_node = process_tree.ProcessTree(label=None)
                new_node.parent = root_loop
                root_loop._children.append(copy.copy(new_node))

            else:
                new_node = process_tree.ProcessTree(label=activity)
                new_node.parent = root_loop
                root_loop._children.append(copy.copy(new_node))
                activity = self.get_next_activity(activity)
            new_node = process_tree.ProcessTree(label=activity)
            new_node.parent = root
            root._children.append(copy.copy(new_node))
            self.total_activities -= 1
        else:
            if silent_activity and operator == "choice":
                number = random.choice([0, 1])
                if number == 0:
                    new_node = process_tree.ProcessTree(label=None)
                    new_node.parent = root
                    root._children.append(copy.copy(new_node))
                    new_node = process_tree.ProcessTree(label=activity)
                    new_node.parent = root
                    root._children.append(copy.copy(new_node))
                else:
                    new_node = process_tree.ProcessTree(label=activity)
                    new_node.parent = root
                    root._children.append(copy.copy(new_node))
                    new_node = process_tree.ProcessTree(label=None)
                    new_node.parent = root
                    root._children.append(copy.copy(new_node))
            else:
                new_node = process_tree.ProcessTree(label=activity)
                new_node.parent = root
                root._children.append(copy.copy(new_node))
                activity = self.get_next_activity(activity)
                new_node = process_tree.ProcessTree(label=activity)
                new_node.parent = root
                root._children.append(copy.copy(new_node))
        # always two children are added
        self.total_activities -= 2
        return self.get_next_activity(activity)

    def add_node(self, next_activity):
        """
        Add nodes to current tree. The general procedure is as follows:
        Select a random leaf (leaves have label). Next step, and opertor is chosen.
        The chosen operator then replaces the leaf, whereby the old label is then add as a leaf to the manipulated node.
        Then, next activity is added as a second leaf to the new operator node or a silent acticity (tau) is added.
        :return: Next activity
        """
        # Need to select random node that is not a silent activity
        leaf_silent = True
        while (leaf_silent):
            leaf = random.choice(self.tree._get_leaves())
            if leaf.label is not None:
                leaf_silent = False
        operator_nok = True
        while (operator_nok):
            operator = self.select_operator()
            if self.total_activities > 1:
                operator_nok = False
            else:
                if operator != "loop":
                    operator_nok = False
        activity = leaf._get_label()
        leaf._set_label(None)
        leaf._set_operator(assign_operator(operator))
        # Will be an tau added?
        silent_activity = False
        if random.random() < self.parameters["silent"]:
            silent_activity = True
        # add two children
        if operator == "loop":
            leaf._set_operator(pt_operator.Operator.SEQUENCE)
            root_loop = process_tree.ProcessTree(pt_operator.Operator.LOOP)
            root_loop.parent = leaf
            leaf._children.append(copy.copy(root_loop))
            new_node = process_tree.ProcessTree(label=activity)
            new_node.parent = root_loop
            root_loop._children.append(copy.copy(new_node))
            activity = next_activity
            if silent_activity:
                new_node = process_tree.ProcessTree(label=None)
                new_node.parent = root_loop
                root_loop._children.append(copy.copy(new_node))
            else:
                new_node = process_tree.ProcessTree(label=activity)
                new_node.parent = root_loop
                root_loop._children.append(copy.copy(new_node))
                activity = self.get_next_activity(activity)
            new_node = process_tree.ProcessTree(label=activity)
            new_node.parent = leaf
            leaf._children.append(copy.copy(new_node))
            self.total_activities -= 1
        else:
            if silent_activity and operator == "choice":
                number = random.choice([0, 1])
                if number == 0:
                    new_node = process_tree.ProcessTree(label=None)
                    new_node.parent = leaf
                    leaf._children.append(copy.copy(new_node))
                    new_node = process_tree.ProcessTree(label=activity)
                    new_node.parent = leaf
                    leaf._children.append(copy.copy(new_node))
                else:
                    new_node = process_tree.ProcessTree(label=activity)
                    new_node.parent = leaf
                    leaf._children.append(copy.copy(new_node))
                    new_node = process_tree.ProcessTree(label=None)
                    new_node.parent = leaf
                    leaf._children.append(copy.copy(new_node))
            else:
                new_node = process_tree.ProcessTree(label=activity)
                new_node.parent = leaf
                leaf._children.append(copy.copy(new_node))
                activity = next_activity
                new_node = process_tree.ProcessTree(label=activity)
                new_node.parent = leaf
                leaf._children.append(copy.copy(new_node))

        self.total_activities -= 2
        if silent_activity and operator == "choice":
            return next_activity
        else:
            return self.get_next_activity(activity)

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

    def create_process_tree(self):
        self.tree = process_tree.ProcessTree()
        self.set_activity_labels = []
        p = 1
        # create labels
        while (self.total_activities > len(self.set_activity_labels)):
            # pairwise product
            l = itertools.product(self.alphabet, repeat=p)
            for item in l:
                label = ""
                for element in item:
                    label += str(element)
                self.set_activity_labels.append(label)
            p += 1
        step = 1
        activity = self.assign_root_opeartor()
        step += 1

        while (self.total_activities > 0):
            activity = self.add_node(activity)
            step += 1

    def __init__(self, parameters):
        self.parameters = parameters
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
        self.total_activities = int(math.ceil(self.draw_random_number_from_distribution()))


    def generate(self):
        # Create a process tree based on the given probabilities
        self.create_process_tree()
        # add duplicates
        self.add_duplicates()

        return self.tree


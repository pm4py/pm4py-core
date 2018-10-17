import random
import string
from copy import deepcopy

from pm4py.objects import petri


# Generate a Petri net with an initial marking that is a workflow net
class SubtreeGenerator(object):
    def __init__(self, min_no_activities_per_subtree, max_no_activities_per_subtree, max_no_subtrees,
                 prob_spawn_subtree, prob_auto_skip, prob_auto_loop, possible_behaviors):
        """
        Constructor

        Parameters
        ----------
        min_no_activities_per_subtree
            Minimum number of attributes per distinct subtree
        max_no_activities_per_subtree
            Maximum number of attributes per distinct subtree
        max_no_subtrees
            Maximum number of subtrees that should be added to the Petri net
        prob_spawn_subtree
            Probability of spawn of a new subtree
        prob_auto_skip
            Probability of adding a hidden transition that skips the current subtree
        prob_auto_loop
            Probability of adding a hidden transition that loops on the current subtree
        possible_behaviors
            Possible behaviors admitted (sequential, concurrent, parallel, flower)
        """
        self.minNoOfActivitiesPerSubtree = min_no_activities_per_subtree
        self.maxNoOfActivitiesPerSubtree = max_no_activities_per_subtree
        self.maxNoOfSubtrees = max_no_subtrees
        self.probSpawnSubtree = prob_spawn_subtree
        self.probAutoSkip = prob_auto_skip
        self.probAutoLoop = prob_auto_loop
        self.possible_behaviors = possible_behaviors
        self.lastAddedPlace = None
        self.generated_string = False
        self.noOfPlaces = 0
        self.noOfHiddenTrans = 0
        self.noOfSubtrees = 0
        self.addedActivities = set()
        self.net = petri.petrinet.PetriNet()
        self.startPlace = petri.petrinet.PetriNet.Place('start')
        self.net.places.add(self.startPlace)
        self.simulate_net()

        if len(self.lastAddedPlace.out_arcs) > 0:
            self.noOfPlaces = self.noOfPlaces + 1
            new_end_place = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
            self.net.places.add(new_end_place)
            self.noOfHiddenTrans = self.noOfHiddenTrans + 1
            end_trans = petri.petrinet.PetriNet.Transition('skipFinal_' + str(self.noOfHiddenTrans), None)
            self.net.transitions.add(end_trans)
            self.noOfHiddenTrans = self.noOfHiddenTrans + 1
            petri.utils.add_arc_from_to(self.lastAddedPlace, end_trans, self.net)
            petri.utils.add_arc_from_to(end_trans, new_end_place, self.net)
            self.lastAddedPlace = new_end_place

        self.lastAddedPlace.name = "end"

    def generate_string(self, n_letters):
        """
        Generate random string

        Parameters
        ----------
        n_letters
            Number of letters of the string
        """
        self.generated_string = True
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n_letters))

    def generate_activity(self):
        """
        Generate an activity name
        """
        activity_name = ""
        for i in range(100000):
            activity_name = self.generate_string(4)
            if activity_name not in self.addedActivities:
                self.addedActivities.add(activity_name)
                break
        return activity_name

    def simulate_net(self):
        """
        Starts the net simulation
        """
        self.add_subtree(self.startPlace, 0)

    def add_subtree(self, subtree_source_node, rec_depth, subtree_target_node=None, chosen_behavior=None):
        """
        Recursive function that adds subtrees to the Petri net

        Parameters
        ----------
        subtree_source_node
            Source node of the current subtree
        rec_depth
            Reached recursion depth
        subtree_target_node
            (If specified) Target node of the subtree (it should attach to)
        chosen_behavior
            (If specified) Chosen behavior for the current subtree
        """
        num_of_activities_this_subtree = 0
        num_of_child_subtrees = 0
        activities_names = []
        added_transitions = []
        subtrees_types = []
        self.noOfSubtrees = self.noOfSubtrees + 1
        this_possible_behaviors = deepcopy(self.possible_behaviors)
        if rec_depth == 0:
            if "flower" in this_possible_behaviors:
                del this_possible_behaviors[this_possible_behaviors.index("flower")]
        if len(this_possible_behaviors) == 0:
            this_possible_behaviors.append("sequential")
        if chosen_behavior is None:
            chosen_behavior = random.choice(this_possible_behaviors)
        if chosen_behavior == "sequential" or chosen_behavior == "flower":
            for i in range(10000):
                if num_of_activities_this_subtree >= self.minNoOfActivitiesPerSubtree:
                    break
                num_of_activities_this_subtree = random.randrange(0, self.maxNoOfActivitiesPerSubtree)
            for i in range(num_of_activities_this_subtree):
                activity_name = self.generate_activity()
                activities_names.append(activity_name)
                trans = petri.petrinet.PetriNet.Transition(activity_name, activity_name)
                self.net.transitions.add(trans)
                added_transitions.append(trans)
        if chosen_behavior == "concurrent" or chosen_behavior == "parallel":
            num_of_child_subtrees = 0
            for i in range(100000):
                if num_of_child_subtrees >= self.minNoOfActivitiesPerSubtree:
                    break
                num_of_child_subtrees = random.randrange(0, self.maxNoOfActivitiesPerSubtree)
            for i in range(num_of_child_subtrees):
                if self.noOfSubtrees >= self.maxNoOfSubtrees:
                    subtrees_types.append("sequential")
                else:
                    subtrees_types.append(random.choice(this_possible_behaviors))
        if chosen_behavior == "sequential":
            next_source_node = subtree_source_node
            for i in range(num_of_activities_this_subtree):
                petri.utils.add_arc_from_to(next_source_node, added_transitions[i], self.net)
                if i == num_of_activities_this_subtree - 1 and subtree_target_node is not None and type(
                        subtree_target_node) is petri.petrinet.PetriNet.Place:
                    next_source_node = subtree_target_node
                else:
                    self.noOfPlaces = self.noOfPlaces + 1
                    next_source_node = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
                    self.lastAddedPlace = next_source_node
                    self.net.places.add(next_source_node)
                petri.utils.add_arc_from_to(added_transitions[i], next_source_node, self.net)
            r = random.random()
            if r < self.probSpawnSubtree and self.noOfSubtrees < self.maxNoOfSubtrees:
                self.add_subtree(self.lastAddedPlace, rec_depth + 1, subtree_target_node=subtree_target_node)
            if subtree_target_node is not None and type(subtree_target_node) is petri.petrinet.PetriNet.Transition:
                petri.utils.add_arc_from_to(self.lastAddedPlace, subtree_target_node, self.net)
            if subtree_target_node is not None and type(subtree_target_node) is petri.petrinet.PetriNet.Place:
                self.lastAddedPlace = subtree_target_node
        elif chosen_behavior == "flower":
            self.noOfPlaces = self.noOfPlaces + 1
            intermediate_place = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
            self.net.places.add(intermediate_place)
            if subtree_target_node is not None and type(subtree_target_node) is petri.petrinet.PetriNet.Place:
                target_place = subtree_target_node
            else:
                self.noOfPlaces = self.noOfPlaces + 1
                target_place = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
                self.net.places.add(target_place)
            for i in range(num_of_activities_this_subtree):
                petri.utils.add_arc_from_to(subtree_source_node, added_transitions[i], self.net)
                petri.utils.add_arc_from_to(added_transitions[i], intermediate_place, self.net)
            self.noOfHiddenTrans = self.noOfHiddenTrans + 1
            skip_trans = petri.petrinet.PetriNet.Transition(
                'skipFlower' + str(rec_depth) + '_' + str(self.noOfHiddenTrans), None)
            self.net.transitions.add(skip_trans)
            petri.utils.add_arc_from_to(subtree_source_node, skip_trans, self.net)
            petri.utils.add_arc_from_to(skip_trans, intermediate_place, self.net)
            if not (subtree_source_node.name == "start"):
                self.noOfHiddenTrans = self.noOfHiddenTrans + 1
                loop_trans = petri.petrinet.PetriNet.Transition(
                    'loopFlower' + str(rec_depth) + '_' + str(self.noOfHiddenTrans), None)
                self.net.transitions.add(loop_trans)
                petri.utils.add_arc_from_to(loop_trans, subtree_source_node, self.net)
                petri.utils.add_arc_from_to(intermediate_place, loop_trans, self.net)
            self.noOfHiddenTrans = self.noOfHiddenTrans + 1
            tau_trans = petri.petrinet.PetriNet.Transition(
                'tauFlower' + str(rec_depth) + '_' + str(self.noOfHiddenTrans), None)
            self.net.transitions.add(tau_trans)
            petri.utils.add_arc_from_to(intermediate_place, tau_trans, self.net)
            petri.utils.add_arc_from_to(tau_trans, target_place, self.net)
            r = random.random()
            if r < self.probSpawnSubtree and self.noOfSubtrees < self.maxNoOfSubtrees:
                self.add_subtree(intermediate_place, rec_depth + 1, subtree_target_node=target_place)
            if subtree_target_node is not None and type(subtree_target_node) is petri.petrinet.PetriNet.Transition:
                petri.utils.add_arc_from_to(target_place, subtree_target_node, self.net)
            self.lastAddedPlace = target_place
            if subtree_target_node is not None and type(subtree_target_node) is petri.petrinet.PetriNet.Place:
                self.lastAddedPlace = subtree_target_node
        elif chosen_behavior == "concurrent":
            self.noOfPlaces = self.noOfPlaces + 1
            connection_node = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
            self.net.places.add(connection_node)
            for i in range(num_of_child_subtrees):
                self.add_subtree(subtree_source_node, rec_depth + 1, subtree_target_node=connection_node,
                                 chosen_behavior=subtrees_types[i])
            if subtree_target_node is not None and type(subtree_target_node) is petri.petrinet.PetriNet.Transition:
                petri.utils.add_arc_from_to(connection_node, subtree_target_node, self.net)
            if subtree_target_node is not None and type(subtree_target_node) is petri.petrinet.PetriNet.Place:
                self.noOfHiddenTrans = self.noOfHiddenTrans + 1
                hidden_trans = petri.petrinet.PetriNet.Transition(
                    'tauConcurrent' + str(rec_depth) + '_' + str(self.noOfHiddenTrans), None)
                self.net.transitions.add(hidden_trans)
                petri.utils.add_arc_from_to(connection_node, hidden_trans, self.net)
                petri.utils.add_arc_from_to(hidden_trans, subtree_target_node, self.net)
            self.lastAddedPlace = connection_node
            if subtree_target_node is not None and type(subtree_target_node) is petri.petrinet.PetriNet.Place:
                self.lastAddedPlace = subtree_target_node
        elif chosen_behavior == "parallel":
            self.noOfPlaces = self.noOfPlaces + 1
            connection_node = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
            self.net.places.add(connection_node)
            self.noOfHiddenTrans = self.noOfHiddenTrans + 1
            tau_parallel_join = petri.petrinet.PetriNet.Transition(
                'tauParallelJoin' + str(rec_depth) + '_' + str(self.noOfHiddenTrans), None)
            self.net.transitions.add(tau_parallel_join)
            petri.utils.add_arc_from_to(tau_parallel_join, connection_node, self.net)
            self.noOfHiddenTrans = self.noOfHiddenTrans + 1
            tau_parallel_split = petri.petrinet.PetriNet.Transition(
                'tauParallelSplit' + str(rec_depth) + '_' + str(self.noOfHiddenTrans), None)
            self.net.transitions.add(tau_parallel_split)
            petri.utils.add_arc_from_to(subtree_source_node, tau_parallel_split, self.net)
            for i in range(num_of_child_subtrees):
                self.noOfPlaces = self.noOfPlaces + 1
                this_index_source_node = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
                self.net.places.add(this_index_source_node)
                petri.utils.add_arc_from_to(tau_parallel_split, this_index_source_node, self.net)
                self.add_subtree(this_index_source_node, rec_depth + 1, subtree_target_node=tau_parallel_join,
                                 chosen_behavior=subtrees_types[i])
            if subtree_target_node is not None and type(subtree_target_node) is petri.petrinet.PetriNet.Transition:
                petri.utils.add_arc_from_to(connection_node, subtree_target_node, self.net)
            if subtree_target_node is not None and type(subtree_target_node) is petri.petrinet.PetriNet.Place:
                self.noOfHiddenTrans = self.noOfHiddenTrans + 1
                hidden_trans = petri.petrinet.PetriNet.Transition(
                    'tauParFinal' + str(rec_depth) + '_' + str(self.noOfHiddenTrans), None)
                self.net.transitions.add(hidden_trans)
                petri.utils.add_arc_from_to(connection_node, hidden_trans, self.net)
                petri.utils.add_arc_from_to(hidden_trans, subtree_target_node, self.net)
            self.lastAddedPlace = connection_node
            if subtree_target_node is not None and type(subtree_target_node) is petri.petrinet.PetriNet.Place:
                self.lastAddedPlace = subtree_target_node
        if not chosen_behavior == "flower":
            r = random.random()
            if r < self.probAutoSkip:
                self.noOfHiddenTrans = self.noOfHiddenTrans + 1
                auto_skip = petri.petrinet.PetriNet.Transition(
                    'autoSkip' + str(rec_depth) + '_' + str(self.noOfHiddenTrans), None)
                self.net.transitions.add(auto_skip)
                petri.utils.add_arc_from_to(subtree_source_node, auto_skip, self.net)
                petri.utils.add_arc_from_to(auto_skip, self.lastAddedPlace, self.net)
            if not (subtree_source_node.name == "start"):
                r = random.random()
                if r < self.probAutoLoop:
                    self.noOfHiddenTrans = self.noOfHiddenTrans + 1
                    auto_loop = petri.petrinet.PetriNet.Transition(
                        'autoLoop' + str(rec_depth) + '_' + str(self.noOfHiddenTrans), None)
                    self.net.transitions.add(auto_loop)
                    petri.utils.add_arc_from_to(auto_loop, subtree_source_node, self.net)
                    petri.utils.add_arc_from_to(self.lastAddedPlace, auto_loop, self.net)


def generate_petri(nin_no_activities_per_subtree=2, max_no_activities_per_subtree=6, max_no_subtrees=5,
                   prob_spawn_subtree=0.6, prob_auto_skip=0.35, prob_auto_loop=0.0, possible_behaviors=None):
    """
    Generate workflow net

    Parameters
    ----------
    nin_no_activities_per_subtree
        Minimum number of attributes per distinct subtree
    max_no_activities_per_subtree
        Maximum number of attributes per distinct subtree
    max_no_subtrees
        Maximum number of subtrees that should be added to the Petri net
    prob_spawn_subtree
        Probability of spawn of a new subtree
    prob_auto_skip
        Probability of adding a hidden transition that skips the current subtree
    prob_auto_loop
        Probability of adding a hidden transition that loops on the current subtree
    possible_behaviors
        Possible behaviors admitted (sequential, concurrent, parallel, flower)
    """
    if possible_behaviors is None:
        possible_behaviors = ["sequential", "concurrent", "flower", "parallel"]
    stg = SubtreeGenerator(nin_no_activities_per_subtree, max_no_activities_per_subtree, max_no_subtrees,
                           prob_spawn_subtree, prob_auto_skip, prob_auto_loop, possible_behaviors)
    marking = petri.petrinet.Marking({stg.startPlace: 1})
    final_marking = petri.petrinet.Marking({stg.lastAddedPlace: 1})
    return stg.net, marking, final_marking


def apply(parameters=None):
    """
    Generate a Petri net

    Parameters
    ----------
    parameters
        Parameters for the algorithm:
        minNoOfActivitiesPerSubtree -> Minimum number of attributes per distinct subtree
        maxNoOfActivitiesPerSubtree -> Maximum number of attributes per distinct subtree
        maxNoOfSubtrees -> Maximum number of subtrees that should be added to the Petri net
        probSpawnSubtree -> Probability of spawn of a new subtree
        probAutoSkip -> Probability of adding a hidden transition that skips the current subtree
        probAutoLoop -> Probability of adding a hidden transition that loops on the current subtree
        possible_behaviors -> Possible behaviors admitted (sequential, concurrent, parallel, flower)
    """
    if parameters is None:
        parameters = {}
    min_no_of_activities_per_subtree = 2
    max_no_of_activities_per_subtree = 6
    max_no_of_subtrees = 5
    prob_spawn_subtree = 0.6
    prob_auto_skip = 0.35
    prob_auto_loop = 0.0
    possible_behaviors = ["sequential", "concurrent", "flower", "parallel"]
    if "minNoOfActivitiesPerSubtree" in parameters:
        min_no_of_activities_per_subtree = parameters["minNoOfActivitiesPerSubtree"]
    if "maxNoOfSubtrees" in parameters:
        max_no_of_subtrees = parameters["maxNoOfSubtrees"]
    if "probSpawnSubtree" in parameters:
        prob_spawn_subtree = parameters["probSpawnSubtree"]
    if "probAutoSkip" in parameters:
        prob_auto_skip = parameters["probAutoSkip"]
    if "probAutoLoop" in parameters:
        prob_auto_loop = parameters["probAutoLoop"]
    if "possible_behaviors" in parameters:
        possible_behaviors = parameters["possible_behaviors"]
    return generate_petri(nin_no_activities_per_subtree=min_no_of_activities_per_subtree,
                          max_no_activities_per_subtree=max_no_of_activities_per_subtree,
                          max_no_subtrees=max_no_of_subtrees, prob_spawn_subtree=prob_spawn_subtree,
                          prob_auto_skip=prob_auto_skip, prob_auto_loop=prob_auto_loop,
                          possible_behaviors=possible_behaviors)

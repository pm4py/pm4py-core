from pm4py.entities import petri
import random
import string
from copy import copy, deepcopy

# Generate a Petri net with an initial marking that is a workflow net
class SubtreeGenerator(object):
    def __init__(self, minNoOfActivitiesPerSubtree, maxNoOfActivitiesPerSubtree, maxNoOfSubtrees, probSpawnSubtree, probAutoSkip, probAutoLoop, possible_behaviors):
        """
        Constructor

        Parameters
        ----------
        minNoOfActivitiesPerSubtree
            Minimum number of attributes per distinct subtree
        maxNoOfActivitiesPerSubtree
            Maximum number of attributes per distinct subtree
        maxNoOfSubtrees
            Maximum number of subtrees that should be added to the Petri net
        probSpawnSubtree
            Probability of spawn of a new subtree
        probAutoSkip
            Probability of adding a hidden transition that skips the current subtree
        probAutoLoop
            Probability of adding a hidden transition that loops on the current subtree
        possible_behaviors
            Possible behaviors admitted (sequential, concurrent, parallel, flower)
        """
        self.minNoOfActivitiesPerSubtree = minNoOfActivitiesPerSubtree
        self.maxNoOfActivitiesPerSubtree = maxNoOfActivitiesPerSubtree
        self.maxNoOfSubtrees = maxNoOfSubtrees
        self.probSpawnSubtree = probSpawnSubtree
        self.probAutoSkip = probAutoSkip
        self.probAutoLoop = probAutoLoop
        self.possible_behaviors = possible_behaviors
        self.lastAddedPlace = None
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
            newEndPlace = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
            self.net.places.add(newEndPlace)
            self.noOfHiddenTrans = self.noOfHiddenTrans + 1
            endTrans = petri.petrinet.PetriNet.Transition('skipFinal_' + str(self.noOfHiddenTrans), None)
            self.net.transitions.add(endTrans)
            self.noOfHiddenTrans = self.noOfHiddenTrans + 1
            petri.utils.add_arc_from_to(self.lastAddedPlace, endTrans, self.net)
            petri.utils.add_arc_from_to(endTrans, newEndPlace, self.net)
            self.lastAddedPlace = newEndPlace

        self.lastAddedPlace.name = "end"

    def generate_string(self, N):
        """
        Generate random string

        Parameters
        ----------
        N
            Number of letters of the string
        """
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

    def generate_activity(self):
        """
        Generate an activity name
        """
        while True:
            activity_name = self.generate_string(4)
            if not activity_name in self.addedActivities:
                self.addedActivities.add(activity_name)
                return activity_name

    def simulate_net(self):
        """
        Starts the net simulation
        """
        self.add_subtree(self.startPlace, 0)

    def add_subtree(self, subtreeSourceNode, recDepth, subtreeTargetNode=None, chosenBehavior=None):
        """
        Recursive function that adds subtrees to the Petri net

        Parameters
        ----------
        subtreeSourceNode
            Source node of the current subtree
        recDepth
            Reached recursion depth
        subtreeTargetNode
            (If specified) Target node of the subtree (it should attach to)
        chosenBehavior
            (If specified) Chosen behavior for the current subtree
        """
        self.noOfSubtrees = self.noOfSubtrees + 1
        thisPossibleBehaviors = deepcopy(self.possible_behaviors)
        if recDepth == 0:
            if "flower" in thisPossibleBehaviors:
                del thisPossibleBehaviors[thisPossibleBehaviors.index("flower")]
        if len(thisPossibleBehaviors) == 0:
            thisPossibleBehaviors.append("sequential")
        if chosenBehavior is None:
            chosenBehavior = random.choice(thisPossibleBehaviors)
        if chosenBehavior == "sequential" or chosenBehavior == "flower":
            numOfActivitiesThisSubtree = 0
            while numOfActivitiesThisSubtree < self.minNoOfActivitiesPerSubtree:
                numOfActivitiesThisSubtree = random.randrange(0, self.maxNoOfActivitiesPerSubtree)
            activitiesNames = []
            addedTransitions = []
            i = 0
            while i < numOfActivitiesThisSubtree:
                activityName = self.generate_activity()
                activitiesNames.append(activityName)
                trans = petri.petrinet.PetriNet.Transition(activityName, activityName)
                self.net.transitions.add(trans)
                addedTransitions.append(trans)
                i = i + 1
        if chosenBehavior == "concurrent" or chosenBehavior == "parallel":
            numOfChildSubtrees = 0
            while numOfChildSubtrees < self.minNoOfActivitiesPerSubtree:
                numOfChildSubtrees = random.randrange(0, self.maxNoOfActivitiesPerSubtree)
            subtreesTypes = []
            for i in range(numOfChildSubtrees):
                if self.noOfSubtrees >= self.maxNoOfSubtrees:
                    subtreesTypes.append("sequential")
                else:
                    subtreesTypes.append(random.choice(thisPossibleBehaviors))
        if chosenBehavior == "sequential":
            nextSourceNode = subtreeSourceNode
            for i in range(numOfActivitiesThisSubtree):
                petri.utils.add_arc_from_to(nextSourceNode, addedTransitions[i], self.net)
                if i == numOfActivitiesThisSubtree-1 and subtreeTargetNode is not None and type(subtreeTargetNode) is petri.petrinet.PetriNet.Place:
                    nextSourceNode = subtreeTargetNode
                else:
                    self.noOfPlaces = self.noOfPlaces + 1
                    nextSourceNode = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
                    self.lastAddedPlace = nextSourceNode
                    self.net.places.add(nextSourceNode)
                petri.utils.add_arc_from_to(addedTransitions[i], nextSourceNode, self.net)
            r = random.random()
            if r < self.probSpawnSubtree and self.noOfSubtrees < self.maxNoOfSubtrees:
                self.add_subtree(self.lastAddedPlace, recDepth + 1, subtreeTargetNode=subtreeTargetNode)
            if subtreeTargetNode is not None and type(subtreeTargetNode) is petri.petrinet.PetriNet.Transition:
                petri.utils.add_arc_from_to(self.lastAddedPlace, subtreeTargetNode, self.net)
            if subtreeTargetNode is not None and type(subtreeTargetNode) is petri.petrinet.PetriNet.Place:
                self.lastAddedPlace = subtreeTargetNode
        elif chosenBehavior == "flower":
            self.noOfPlaces = self.noOfPlaces + 1
            intermediatePlace = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
            self.net.places.add(intermediatePlace)
            if subtreeTargetNode is not None and type(subtreeTargetNode) is petri.petrinet.PetriNet.Place:
                targetPlace = subtreeTargetNode
            else:
                self.noOfPlaces = self.noOfPlaces + 1
                targetPlace = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
                self.net.places.add(targetPlace)
            for i in range(numOfActivitiesThisSubtree):
                petri.utils.add_arc_from_to(subtreeSourceNode, addedTransitions[i], self.net)
                petri.utils.add_arc_from_to(addedTransitions[i], intermediatePlace, self.net)
            self.noOfHiddenTrans = self.noOfHiddenTrans + 1
            skipTrans = petri.petrinet.PetriNet.Transition('skipFlower' + str(recDepth) + '_' + str(self.noOfHiddenTrans), None)
            self.net.transitions.add(skipTrans)
            petri.utils.add_arc_from_to(subtreeSourceNode, skipTrans, self.net)
            petri.utils.add_arc_from_to(skipTrans, intermediatePlace, self.net)
            if not(subtreeSourceNode.name == "start"):
                self.noOfHiddenTrans = self.noOfHiddenTrans + 1
                loopTrans = petri.petrinet.PetriNet.Transition('loopFlower' + str(recDepth) + '_' + str(self.noOfHiddenTrans), None)
                self.net.transitions.add(loopTrans)
                petri.utils.add_arc_from_to(loopTrans, subtreeSourceNode, self.net)
                petri.utils.add_arc_from_to(intermediatePlace, loopTrans, self.net)
            self.noOfHiddenTrans = self.noOfHiddenTrans + 1
            tauTrans = petri.petrinet.PetriNet.Transition('tauFlower' + str(recDepth) + '_' + str(self.noOfHiddenTrans), None)
            self.net.transitions.add(tauTrans)
            petri.utils.add_arc_from_to(intermediatePlace, tauTrans, self.net)
            petri.utils.add_arc_from_to(tauTrans, targetPlace, self.net)
            r = random.random()
            if r < self.probSpawnSubtree and self.noOfSubtrees < self.maxNoOfSubtrees:
                self.add_subtree(intermediatePlace, recDepth + 1, subtreeTargetNode=targetPlace)
            if subtreeTargetNode is not None and type(subtreeTargetNode) is petri.petrinet.PetriNet.Transition:
                petri.utils.add_arc_from_to(targetPlace, subtreeTargetNode, self.net)
            self.lastAddedPlace = targetPlace
            if subtreeTargetNode is not None and type(subtreeTargetNode) is petri.petrinet.PetriNet.Place:
                self.lastAddedPlace = subtreeTargetNode
        elif chosenBehavior == "concurrent":
            self.noOfPlaces = self.noOfPlaces + 1
            connectionNode = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
            self.net.places.add(connectionNode)
            for i in range(numOfChildSubtrees):
                self.add_subtree(subtreeSourceNode, recDepth+1, subtreeTargetNode=connectionNode, chosenBehavior=subtreesTypes[i])
            if subtreeTargetNode is not None and type(subtreeTargetNode) is petri.petrinet.PetriNet.Transition:
                petri.utils.add_arc_from_to(connectionNode, subtreeTargetNode, self.net)
            if subtreeTargetNode is not None and type(subtreeTargetNode) is petri.petrinet.PetriNet.Place:
                self.noOfHiddenTrans = self.noOfHiddenTrans + 1
                hiddenTrans = petri.petrinet.PetriNet.Transition('tauConcurrent' + str(recDepth) + '_' + str(self.noOfHiddenTrans), None)
                self.net.transitions.add(hiddenTrans)
                petri.utils.add_arc_from_to(connectionNode, hiddenTrans, self.net)
                petri.utils.add_arc_from_to(hiddenTrans, subtreeTargetNode, self.net)
            self.lastAddedPlace = connectionNode
            if subtreeTargetNode is not None and type(subtreeTargetNode) is petri.petrinet.PetriNet.Place:
                self.lastAddedPlace = subtreeTargetNode
        elif chosenBehavior == "parallel":
            self.noOfPlaces = self.noOfPlaces + 1
            connectionNode = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
            self.net.places.add(connectionNode)
            self.noOfHiddenTrans = self.noOfHiddenTrans + 1
            tauParallelJoin = petri.petrinet.PetriNet.Transition('tauParallelJoin' + str(recDepth) + '_' + str(self.noOfHiddenTrans), None)
            self.net.transitions.add(tauParallelJoin)
            petri.utils.add_arc_from_to(tauParallelJoin, connectionNode, self.net)
            self.noOfHiddenTrans = self.noOfHiddenTrans + 1
            tauParallelSplit = petri.petrinet.PetriNet.Transition(
                'tauParallelSplit' + str(recDepth) + '_' + str(self.noOfHiddenTrans), None)
            self.net.transitions.add(tauParallelSplit)
            petri.utils.add_arc_from_to(subtreeSourceNode, tauParallelSplit, self.net)
            for i in range(numOfChildSubtrees):
                self.noOfPlaces = self.noOfPlaces + 1
                thisIndexSourceNode = petri.petrinet.PetriNet.Place('p' + str(self.noOfPlaces))
                self.net.places.add(thisIndexSourceNode)
                petri.utils.add_arc_from_to(tauParallelSplit, thisIndexSourceNode, self.net)
                self.add_subtree(thisIndexSourceNode, recDepth + 1, subtreeTargetNode=tauParallelJoin, chosenBehavior=subtreesTypes[i])
            if subtreeTargetNode is not None and type(subtreeTargetNode) is petri.petrinet.PetriNet.Transition:
                petri.utils.add_arc_from_to(connectionNode, subtreeTargetNode, self.net)
            if subtreeTargetNode is not None and type(subtreeTargetNode) is petri.petrinet.PetriNet.Place:
                self.noOfHiddenTrans = self.noOfHiddenTrans + 1
                hiddenTrans = petri.petrinet.PetriNet.Transition('tauParFinal' + str(recDepth) + '_' + str(self.noOfHiddenTrans), None)
                self.net.transitions.add(hiddenTrans)
                petri.utils.add_arc_from_to(connectionNode, hiddenTrans, self.net)
                petri.utils.add_arc_from_to(hiddenTrans, subtreeTargetNode, self.net)
            self.lastAddedPlace = connectionNode
            if subtreeTargetNode is not None and type(subtreeTargetNode) is petri.petrinet.PetriNet.Place:
                self.lastAddedPlace = subtreeTargetNode
        if not chosenBehavior == "flower":
            r = random.random()
            if r < self.probAutoSkip:
                self.noOfHiddenTrans = self.noOfHiddenTrans + 1
                autoSkip = petri.petrinet.PetriNet.Transition('autoSkip' + str(recDepth) + '_' + str(self.noOfHiddenTrans), None)
                self.net.transitions.add(autoSkip)
                petri.utils.add_arc_from_to(subtreeSourceNode, autoSkip, self.net)
                petri.utils.add_arc_from_to(autoSkip, self.lastAddedPlace, self.net)
            if not (subtreeSourceNode.name == "start"):
                r = random.random()
                if r < self.probAutoLoop:
                    self.noOfHiddenTrans = self.noOfHiddenTrans + 1
                    autoLoop = petri.petrinet.PetriNet.Transition('autoLoop' + str(recDepth) + '_' + str(self.noOfHiddenTrans), None)
                    self.net.transitions.add(autoLoop)
                    petri.utils.add_arc_from_to(autoLoop, subtreeSourceNode, self.net)
                    petri.utils.add_arc_from_to(self.lastAddedPlace, autoLoop, self.net)

def generate_petri(minNoOfActivitiesPerSubtree=2, maxNoOfActivitiesPerSubtree=6, maxNoOfSubtrees=5, probSpawnSubtree=0.6, probAutoSkip=0.35, probAutoLoop=0.0, possible_behaviors=["sequential","concurrent","flower","parallel"]):
    """
    Generate workflow net

    Parameters
    ----------
    minNoOfActivitiesPerSubtree
        Minimum number of attributes per distinct subtree
    maxNoOfActivitiesPerSubtree
        Maximum number of attributes per distinct subtree
    maxNoOfSubtrees
        Maximum number of subtrees that should be added to the Petri net
    probSpawnSubtree
        Probability of spawn of a new subtree
    probAutoSkip
        Probability of adding a hidden transition that skips the current subtree
    probAutoLoop
        Probability of adding a hidden transition that loops on the current subtree
    possible_behaviors
        Possible behaviors admitted (sequential, concurrent, parallel, flower)
    """
    STG = SubtreeGenerator(minNoOfActivitiesPerSubtree, maxNoOfActivitiesPerSubtree, maxNoOfSubtrees, probSpawnSubtree, probAutoSkip, probAutoLoop, possible_behaviors)
    #STG.simulate_net()
    marking = petri.petrinet.Marking({STG.startPlace: 1})
    final_marking = petri.petrinet.Marking({STG.lastAddedPlace: 1})
    return STG.net, marking, final_marking

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
    #minNoOfActivitiesPerSubtree=2,
    # maxNoOfActivitiesPerSubtree=6, maxNoOfSubtrees=5, probSpawnSubtree=0.6, probAutoSkip=0.35, probAutoLoop=0.0, possible_behaviors=["sequential","concurrent","flower","parallel"]
    minNoOfActivitiesPerSubtree=2
    maxNoOfActivitiesPerSubtree=6
    maxNoOfSubtrees=5
    prowSpawnSubtree=0.6
    probAutoSkip=0.35
    probAutoLoop=0.0
    possible_behaviors = ["sequential","concurrent","flower","parallel"]
    if "minNoOfActivitiesPerSubtree" in parameters:
        minNoOfActivitiesPerSubtree = parameters["minNoOfActivitiesPerSubtree"]
    if "maxNoOfSubtrees" in parameters:
        maxNoOfSubtrees = parameters["maxNoOfSubtrees"]
    if "probSpawnSubtree" in parameters:
        probSpawnSubtree = parameters["probSpawnSubtree"]
    if "probAutoSkip" in parameters:
        probAutoSkip = parameters["probAutoSkip"]
    if "probAutoLoop" in parameters:
        probAutoLoop = parameters["probAutoLoop"]
    if "possible_behaviors" in parameters:
        possible_behaviors = parameters["possible_behaviors"]
    return generate_petri(minNoOfActivitiesPerSubtree=minNoOfActivitiesPerSubtree, maxNoOfSubtrees=maxNoOfSubtrees, probSpawnSubtree=probSpawnSubtree, probAutoSkip=probAutoSkip, probAutoLoop=probAutoLoop, possible_behaviors=possible_behaviors)
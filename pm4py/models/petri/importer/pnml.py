from lxml import etree
import uuid
import time
import inspect
from pm4py.models import petri
from pm4py.models.petri.petrinet import Marking
from copy import copy, deepcopy
import logging
from pm4py.models.petri import visualize as pn_viz
import tempfile, os

def import_petri_from_string(petri_string):
    """
    Import a Petri net from a string

    Parameters
    ----------
    petri_string
        Petri net expressed as PNML string
    """
    fp = tempfile.NamedTemporaryFile(suffix='.pnml')
    fp.close()
    with open(fp.name, 'w') as f:
        f.write(petri_string)
    net = import_petri_from_pnml(fp.name)
    os.remove(fp.name)
    return net

def import_petri_from_pnml(inputFilePath):
    """
    Import a Petri net from a PNML file

    Parameters
    ----------
    inputFilePath
        Input file path
    """
    context = etree.iterparse(inputFilePath, events=['start', 'end'])
    net = petri.petrinet.PetriNet('imported_' + str(time.time()))
    markingDict = {}
    placesDict = {}
    transDict = {}

    readingWhat = ""
    readingId = ""
    readingSource = ""
    readingTarget = ""
    transInvis = False
    isInitialMarking = False
    initialMarkingCount = 0

    for tree_event, elem in context:

        if tree_event == "start":
            if "place" in elem.tag:
                isInitialMarking = False
                readingWhat = "place"
                readingId = elem.get("id")
            elif "transition" in elem.tag:
                readingWhat = "transition"
                readingId = elem.get("id")
                transition = petri.petrinet.PetriNet.Transition(readingId, None)
                transDict[readingId] = transition
            elif "initialMarking" in elem.tag:
                readingWhat = "initialMarking"
            elif "text" in elem.tag:
                elementText = elem.text
                if readingWhat == "place":
                    place = petri.petrinet.PetriNet.Place(elementText)
                    placesDict[readingId] = place
                elif readingWhat == "transition":
                    if not transInvis:
                        transDict[readingId].label = elementText
                    transDict[readingId].name = elementText
                elif readingWhat == "initialMarking":
                    isInitialMarking = True
                    try:
                        initialMarkingCount = int(elementText)
                    except:
                        logging.info("cannot read initial marking number")
                        initialMarkingCount = 0
                    if initialMarkingCount > 0:
                        markingDict[placesDict[readingId]] = initialMarkingCount
            elif "toolspecific" in elem.tag:
                if readingWhat == "transition":
                    activity = elem.get("activity")
                    if "$invisible$" in activity:
                        transInvis = True
                        transDict[readingId].label = None
        if tree_event == "end":
            if "place" in elem.tag:
                readingWhat = 0
                readingWhat = ""
            elif "initialMarking" in elem.tag:
                readingWhat = "place"
            elif "transition" in elem.tag:
                readingWhat = 0
                readingWhat = ""
                transInvis = False
    for placeName in placesDict.keys():
        place = placesDict[placeName]
        net.places.add(place)
    for transId in transDict.keys():
        transition = transDict[transId]
        net.transitions.add(transition)
    context = etree.iterparse(inputFilePath, events=['start', 'end'])
    for tree_event, elem in context:
        if tree_event == "start":
            if "arc" in elem.tag:
                readingWhat = "arc"
                readingId = elem.get("id")
                readingSource = elem.get("source")
                readingTarget = elem.get("target")
                if readingSource in placesDict.keys() and readingTarget in transDict.keys():
                    petri.utils.add_arc_from_to(placesDict[readingSource], transDict[readingTarget], net)
                elif readingTarget in placesDict.keys() and readingSource in transDict.keys():
                    petri.utils.add_arc_from_to(transDict[readingSource], placesDict[readingTarget], net)
        if tree_event == "end":
            if "arc" in elem.tag:
                readingWhat = 0
                readingId = 0
                readingSource = 0
                readingTarget = 0
                readingWhat = ""
                readingId = ""
                readingSource = ""
                readingTarget = ""

    netPlaces = copy(net.places)
    for place in netPlaces:
        if len(place.in_arcs) == 0 and len(place.out_arcs) == 0:
            net.places.remove(place)

    return net, Marking(markingDict)
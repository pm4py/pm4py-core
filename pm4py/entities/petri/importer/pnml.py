from lxml import etree
import time
from pm4py.entities import petri
from pm4py.entities.petri.petrinet import Marking
from copy import copy, deepcopy
import logging
import tempfile, os
from pm4py.entities.petri.common import final_marking

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
    net, initial_marking, final_marking = import_net(fp.name)
    os.remove(fp.name)
    return net, initial_marking, final_marking

def import_net(inputFilePath):
    """
    Import a Petri net from a PNML file

    Parameters
    ----------
    inputFilePath
        Input file path
    """
    tree = etree.parse(inputFilePath)
    root = tree.getroot()

    net = petri.petrinet.PetriNet('imported_' + str(time.time()))
    marking = petri.petrinet.Marking()
    fmarking = petri.petrinet.Marking()

    nett = None
    page = None
    finalmarkings = None

    for child in root:
        nett = child

    placesDict = {}
    transDict = {}

    if nett is not None:
        for child in nett:
            if "page" in child.tag:
                page = child
            if "finalmarkings" in child.tag:
                finalmarkings = child

    if page is not None:
        for child in page:
            if "place" in child.tag:
                id = child.get("id")
                place_name = id
                number = 0
                for child2 in child:
                    if "name" in child2.tag:
                        for child3 in child2:
                            if child3.text:
                                place_name = child3.text
                    if "initialMarking" in child2.tag:
                        for child3 in child2:
                            if child3.tag == "text":
                                number = int(child3.text)
                placesDict[id] = petri.petrinet.PetriNet.Place(place_name)
                net.places.add(placesDict[id])
                if number > 0:
                    marking[placesDict[id]] = number

    if page is not None:
        for child in page:
            if "transition" in child.tag:
                trans_name = child.get("id")
                trans_label = trans_name
                trans_visible = True
                for child2 in child:
                    if child2.tag == "name":
                        for child3 in child2:
                            if child3.text:
                                trans_label = child3.text
                    if "toolspecific" in child2.tag:
                        activity = child2.get("activity")
                        if "invisible" in activity:
                            trans_visible = False
                if not trans_visible:
                    trans_label = None
                transDict[trans_name] = petri.petrinet.PetriNet.Transition(trans_name, trans_label)
                net.transitions.add(transDict[trans_name])

    if page is not None:
        for child in page:
            if "arc" in child.tag:
                arc_source = child.get("source")
                arc_target = child.get("target")

                if arc_source in placesDict and arc_target in transDict:
                    petri.utils.add_arc_from_to(placesDict[arc_source], transDict[arc_target], net)
                elif arc_target in placesDict and arc_source in transDict:
                    petri.utils.add_arc_from_to(transDict[arc_source], placesDict[arc_target], net)

    if finalmarkings is not None:
        for child in finalmarkings:
            for child2 in child:
                id = child2.get("idref")
                for child3 in child2:
                    if "text" in child3.tag:
                        number = int(child3.text)
                        if number > 0:
                            fmarking[placesDict[id]] = number

    # generate the final marking in the case has not been found
    if len(fmarking) == 0:
        fmarking = final_marking.discover_final_marking(net)

    return net, marking, fmarking
import os
import tempfile
import time

from lxml import etree, objectify

from pm4py.objects import petri
from pm4py.objects.petri.common import final_marking
from pm4py.objects.random_variables.random_variable import RandomVariable
from pm4py.util import constants


def import_petri_from_string(petri_string, parameters=None):
    """
    Import a Petri net from a string

    Parameters
    ----------
    petri_string
        Petri net expressed as PNML string
    parameters
        Other parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    fp = tempfile.NamedTemporaryFile(suffix='.pnml')
    fp.close()
    with open(fp.name, 'w') as f:
        f.write(petri_string)
    net, initial_marking, this_final_marking = import_net(fp.name)
    os.remove(fp.name)
    return net, initial_marking, this_final_marking


def import_net(input_file_path, parameters=None):
    """
    Import a Petri net from a PNML file

    Parameters
    ----------
    input_file_path
        Input file path
    parameters
        Other parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    parser = etree.XMLParser(remove_comments=True)
    tree = objectify.parse(input_file_path, parser=parser)
    root = tree.getroot()

    net = petri.petrinet.PetriNet('imported_' + str(time.time()))
    marking = petri.petrinet.Marking()
    fmarking = petri.petrinet.Marking()

    nett = None
    page = None
    finalmarkings = None

    stochastic_information = {}

    for child in root:
        nett = child

    places_dict = {}
    trans_dict = {}

    if nett is not None:
        for child in nett:
            if "page" in child.tag:
                page = child
            if "finalmarkings" in child.tag:
                finalmarkings = child

    if page is None:
        page = nett

    if page is not None:
        for child in page:
            if "place" in child.tag:
                position_X = None
                position_Y = None
                dimension_X = None
                dimension_Y = None
                place_id = child.get("id")
                place_name = place_id
                number = 0
                for child2 in child:
                    if child2.tag.endswith('name'):
                        for child3 in child2:
                            if child3.text:
                                place_name = child3.text
                    if child2.tag.endswith('initialMarking'):
                        for child3 in child2:
                            if child3.tag.endswith("text"):
                                number = int(child3.text)
                    if child2.tag.endswith('graphics'):
                        for child3 in child2:
                            if child3.tag.endswith('position'):
                                position_X = float(child3.get("x"))
                                position_Y = float(child3.get("y"))
                            elif child3.tag.endswith("dimension"):
                                dimension_X = float(child3.get("x"))
                                dimension_Y = float(child3.get("y"))
                places_dict[place_id] = petri.petrinet.PetriNet.Place(place_id)
                places_dict[place_id].properties[constants.PLACE_NAME_TAG] = place_name
                net.places.add(places_dict[place_id])
                if position_X is not None and position_Y is not None and dimension_X is not None and dimension_Y is not None:
                    places_dict[place_id].properties[constants.LAYOUT_INFORMATION_PETRI] = ((position_X, position_Y), (dimension_X, dimension_Y))
                if number > 0:
                    marking[places_dict[place_id]] = number
                del place_name

    if page is not None:
        for child in page:
            if child.tag.endswith("transition"):
                position_X = None
                position_Y = None
                dimension_X = None
                dimension_Y = None
                trans_name = child.get("id")
                trans_label = trans_name
                trans_visible = True

                random_variable = None

                for child2 in child:
                    if child2.tag.endswith("name"):
                        for child3 in child2:
                            if child3.text:
                                if trans_label == trans_name:
                                    trans_label = child3.text
                    if child2.tag.endswith("graphics"):
                        for child3 in child2:
                            if child3.tag.endswith("position"):
                                position_X = float(child3.get("x"))
                                position_Y = float(child3.get("y"))
                            elif child3.tag.endswith("dimension"):
                                dimension_X = float(child3.get("x"))
                                dimension_Y = float(child3.get("y"))
                    if child2.tag.endswith("toolspecific"):
                        tool = child2.get("tool")
                        if "ProM" in tool:
                            activity = child2.get("activity")
                            if "invisible" in activity:
                                trans_visible = False
                        elif "StochasticPetriNet" in tool:
                            distribution_type = None
                            distribution_parameters = None
                            priority = None
                            weight = None

                            for child3 in child2:
                                key = child3.get("key")
                                value = child3.text

                                if key == "distributionType":
                                    distribution_type = value
                                elif key == "distributionParameters":
                                    distribution_parameters = value
                                elif key == "priority":
                                    priority = int(value)
                                elif key == "weight":
                                    weight = float(value)

                            random_variable = RandomVariable()
                            random_variable.read_from_string(distribution_type, distribution_parameters)
                            random_variable.set_priority(priority)
                            random_variable.set_weight(weight)

                if not trans_visible:
                    trans_label = None
                #if "INVISIBLE" in trans_label:
                #    trans_label = None

                trans_dict[trans_name] = petri.petrinet.PetriNet.Transition(trans_name, trans_label)
                net.transitions.add(trans_dict[trans_name])

                if random_variable is not None:
                    trans_dict[trans_name].properties[constants.STOCHASTIC_DISTRIBUTION] = random_variable
                if position_X is not None and position_Y is not None and dimension_X is not None and dimension_Y is not None:
                    trans_dict[trans_name].properties[constants.LAYOUT_INFORMATION_PETRI] = ((position_X, position_Y), (dimension_X, dimension_Y))

    if page is not None:
        for child in page:
            if child.tag.endswith("arc"):
                arc_source = child.get("source")
                arc_target = child.get("target")
                arc_weight = 1

                for arc_child in child:
                    if arc_child.tag.endswith("inscription"):
                        for text_arcweight in arc_child:
                            if text_arcweight.tag.endswith("text"):
                                arc_weight = int(text_arcweight.text)

                if arc_source in places_dict and arc_target in trans_dict:
                    petri.utils.add_arc_from_to(places_dict[arc_source], trans_dict[arc_target], net, weight=arc_weight)
                elif arc_target in places_dict and arc_source in trans_dict:
                    petri.utils.add_arc_from_to(trans_dict[arc_source], places_dict[arc_target], net, weight=arc_weight)

    if finalmarkings is not None:
        for child in finalmarkings:
            for child2 in child:
                place_id = child2.get("idref")
                for child3 in child2:
                    if child3.tag.endswith("text"):
                        number = int(child3.text)
                        if number > 0:
                            fmarking[places_dict[place_id]] = number

    # generate the final marking in the case has not been found
    if len(fmarking) == 0:
        fmarking = final_marking.discover_final_marking(net)

    return net, marking, fmarking

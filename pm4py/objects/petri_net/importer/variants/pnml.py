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
import time

from lxml import etree, objectify

from pm4py.objects.petri_net.utils import final_marking
from pm4py.objects.petri_net.obj import PetriNet, Marking, ResetNet, InhibitorNet, ResetInhibitorNet
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
from pm4py.objects.petri_net import properties as petri_properties
from pm4py.util import constants, exec_utils
import warnings
from enum import Enum


class Parameters(Enum):
    ENCODING = "encoding"
    AUTO_GUESS_FINAL_MARKING = "auto_guess_final_marking"
    RETURN_STOCHASTIC_MAP = "return_stochastic_map"


def import_net(input_file_path, parameters=None):
    """
    Import a Petri net from a PNML file

    Parameters
    ----------
    input_file_path
        Input file path
    parameters
        Other parameters of the algorithm

    Returns
    -----------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, None)

    parser = etree.XMLParser(remove_comments=True, encoding=encoding)

    F = open(input_file_path, "rb")
    tree = objectify.parse(F, parser=parser)
    F.close()

    root = tree.getroot()

    return import_net_from_xml_object(root, parameters=parameters)


def import_net_from_string(petri_string, parameters=None):
    """
    Imports a Petri net from a string

    Parameters
    -------------
    petri_string
        (Binary) string representing the Petri net
    parameters
        Parameters of the algorithm

    Returns
    -----------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    if type(petri_string) is str:
        petri_string = petri_string.encode(constants.DEFAULT_ENCODING)

    parser = etree.XMLParser(remove_comments=True)
    root = objectify.fromstring(petri_string, parser=parser)

    return import_net_from_xml_object(root, parameters=parameters)


def import_net_from_xml_object(root, parameters=None):
    """
    Import a Petri net from an etree XML object

    Parameters
    ----------
    root
        Root object of the XML
    parameters
        Other parameters of the algorithm:
        - AUTO_GUESS_FINAL_MARKING: automatic guessing the final marking from the .pnml file
    """
    if parameters is None:
        parameters = {}

    auto_guess_final_marking = exec_utils.get_param_value(Parameters.AUTO_GUESS_FINAL_MARKING, parameters, True)
    return_stochastic_information = exec_utils.get_param_value(Parameters.RETURN_STOCHASTIC_MAP, parameters, False)

    net = PetriNet('imported_' + str(time.time()))
    marking = Marking()
    fmarking = None

    nett = None
    page = None
    finalmarkings = None
    variables = None

    stochastic_map = {}

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
            if "variables" in child.tag:
                variables = child

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
                places_dict[place_id] = PetriNet.Place(place_id)
                places_dict[place_id].properties[constants.PLACE_NAME_TAG] = place_name
                net.places.add(places_dict[place_id])
                if position_X is not None and position_Y is not None and dimension_X is not None and dimension_Y is not None:
                    places_dict[place_id].properties[constants.LAYOUT_INFORMATION_PETRI] = (
                        (position_X, position_Y), (dimension_X, dimension_Y))
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
                trans_id = child.get("id")
                trans_name = trans_id
                trans_visible = True
                trans_properties = {}
                trans_guard = child.get("guard")
                if trans_guard is not None:
                    trans_properties[petri_properties.TRANS_GUARD] = trans_guard

                random_variable = None

                for child2 in child:
                    if child2.tag.endswith("name"):
                        for child3 in child2:
                            if child3.text:
                                if trans_name == trans_id:
                                    trans_name = child3.text
                    elif child2.tag.endswith("graphics"):
                        for child3 in child2:
                            if child3.tag.endswith("position"):
                                position_X = float(child3.get("x"))
                                position_Y = float(child3.get("y"))
                            elif child3.tag.endswith("dimension"):
                                dimension_X = float(child3.get("x"))
                                dimension_Y = float(child3.get("y"))
                    elif child2.tag.endswith("toolspecific"):
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
                                elif key == "invisible":
                                    if value.lower() == "true":
                                        trans_visible = False

                            from pm4py.objects.random_variables.random_variable import RandomVariable

                            random_variable = RandomVariable()
                            random_variable.read_from_string(distribution_type, distribution_parameters)
                            random_variable.set_priority(priority)
                            random_variable.set_weight(weight)
                    elif child2.tag.endswith(petri_properties.WRITE_VARIABLE):
                        # property for data Petri nets
                        if petri_properties.WRITE_VARIABLE not in trans_properties:
                            trans_properties[petri_properties.WRITE_VARIABLE] = []
                        trans_properties[petri_properties.WRITE_VARIABLE].append(child2.text)
                    elif child2.tag.endswith(petri_properties.READ_VARIABLE):
                        # property for data Petri nets
                        if petri_properties.READ_VARIABLE not in trans_properties:
                            trans_properties[petri_properties.READ_VARIABLE] = []
                        trans_properties[petri_properties.READ_VARIABLE].append(child2.text)

                # 15/02/2021: the name associated in the PNML to invisible transitions was lost.
                # at least save that as property.
                if trans_visible:
                    trans_label = trans_name
                else:
                    trans_label = None

                trans_dict[trans_id] = PetriNet.Transition(trans_id, trans_label)
                trans_dict[trans_id].properties[constants.TRANS_NAME_TAG] = trans_name
                for prop in trans_properties:
                    trans_dict[trans_id].properties[prop] = trans_properties[prop]
                net.transitions.add(trans_dict[trans_id])

                if random_variable is not None:
                    trans_dict[trans_id].properties[constants.STOCHASTIC_DISTRIBUTION] = random_variable
                    stochastic_map[trans_dict[trans_id]] = random_variable

                if position_X is not None and position_Y is not None and dimension_X is not None and dimension_Y is not None:
                    trans_dict[trans_id].properties[constants.LAYOUT_INFORMATION_PETRI] = (
                        (position_X, position_Y), (dimension_X, dimension_Y))

    if page is not None:
        for child in page:
            if child.tag.endswith("arc"):
                arc_source = child.get("source")
                arc_target = child.get("target")
                arc_weight = 1
                arc_type = None
                arc_properties = {}

                for arc_child in child:
                    if arc_child.tag.endswith("inscription"):
                        for text_element in arc_child:
                            if text_element.tag.endswith("text"):
                                arc_weight = int(text_element.text)
                    elif arc_child.tag.endswith(petri_properties.ARCTYPE):
                        for text_element in arc_child:
                            if text_element.tag.endswith("text"):
                                arc_type = text_element.text

                if arc_source in places_dict and arc_target in trans_dict:
                    if arc_type == petri_properties.INHIBITOR_ARC and not isinstance(net, InhibitorNet):
                        if isinstance(net, ResetNet):
                            net = ResetInhibitorNet(name=net.name, places=net.places, transitions=net.transitions, arcs=net.arcs, properties=net.properties)
                        else:
                            net = InhibitorNet(name=net.name, places=net.places, transitions=net.transitions, arcs=net.arcs, properties=net.properties)
                    if arc_type == petri_properties.RESET_ARC and not isinstance(net, ResetNet):
                        if isinstance(net, InhibitorNet):
                            net = ResetInhibitorNet(name=net.name, places=net.places,
                                                    transitions=net.transitions, arcs=net.arcs,
                                                    properties=net.properties)
                        else:
                            net = ResetNet(name=net.name, places=net.places,
                                           transitions=net.transitions, arcs=net.arcs,
                                           properties=net.properties)
                    a = add_arc_from_to(places_dict[arc_source], trans_dict[arc_target], net, weight=arc_weight, type=arc_type)
                    for prop in arc_properties:
                        a.properties[prop] = arc_properties[prop]
                elif arc_target in places_dict and arc_source in trans_dict:
                    a = add_arc_from_to(trans_dict[arc_source], places_dict[arc_target], net, weight=arc_weight, type=arc_type)
                    for prop in arc_properties:
                        a.properties[prop] = arc_properties[prop]

    if finalmarkings is not None:
        fmarking = Marking()
        for child in finalmarkings:
            for child2 in child:
                place_id = child2.get("idref")
                for child3 in child2:
                    if child3.tag.endswith("text"):
                        number = int(child3.text)
                        if number > 0:
                            fmarking[places_dict[place_id]] = number

    if variables is not None:
        net.properties[petri_properties.VARIABLES] = []
        for child in variables:
            variable_type = child.get("type")
            variable_name = ""
            for child2 in child:
                if child2.tag.endswith("name"):
                    variable_name = child2.text
            net.properties[petri_properties.VARIABLES].append({"type": variable_type, "name": variable_name})

    if fmarking is None:
        if auto_guess_final_marking:
            # generate the final marking in the case has not been found
            fmarking = final_marking.discover_final_marking(net)
        else:
            if constants.SHOW_INTERNAL_WARNINGS:
                warnings.warn("the Petri net has been imported without a specified final marking. Please create it using the method pm4py.generate_marking")

    if return_stochastic_information:
        return net, marking, fmarking, stochastic_map

    return net, marking, fmarking

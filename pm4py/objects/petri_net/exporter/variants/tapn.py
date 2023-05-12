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
import uuid

from lxml import etree

from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net import properties as petri_properties
from pm4py.util import constants

def export_petri_tree(petrinet, marking, final_marking=None, export_prom5=False, parameters=None):
    """
    Export a Petrinet to a XML tree.
    VCO: this will become a TAPN that can be imported to TAPAAL

    Parameters
    ----------
    petrinet: :class:`pm4py.entities.petri.petrinet.PetriNet`
        Petri net
    marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Marking
    final_marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Final marking (optional)
    export_prom5
        Enables exporting PNML files in a format that is ProM5-friendly
    parameters
        Other parameters of the algorithm

    Returns
    ----------
    tree
        XML tree
    """
    if parameters is None:
        parameters = {}

    if final_marking is None:
        final_marking = Marking()

    root = etree.Element("pnml")
    root.set("xmlns", "http://www.informatik.hu-berlin.de/top/pnml/ptNetb")
    net = etree.SubElement(root, "net")
    net.set("id", "netFromDCR")
    net.set("type", "P/T net")
    net.set("active", "true")
    page = net
    places_map = {}
    for place in petrinet.places:
        places_map[place] = place.name
        pl = etree.SubElement(page, "place")
        pl.set("id", place.name)
        pl.set("displayName","true")
        pl.set("name",place.name)
        if petri_properties.AGE_INVARIANT in place.properties:
            pl.set("invariant", f"<= {place.properties[petri_properties.AGE_INVARIANT]}")
        else:
            pl.set("invariant","< inf")
        if place in marking:
            pl.set("initialMarking",str(marking[place]))
        else:
            pl.set("initialMarking","0")
        if constants.LAYOUT_INFORMATION_PETRI in place.properties:
            pl.set("positionX", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][0][0]))
            pl.set("positionY", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][0][1]))
        else:
            pl.set("positionX", "0")
            pl.set("positionY", "0")
        pl.set("nameOffsetX","0")
        pl.set("nameOffsetY","0")

    transitions_map = {}
    for transition in petrinet.transitions:
        transitions_map[transition] = transition.name
        trans = etree.SubElement(page, "transition")
        trans.set("angle","0")
        trans.set("displayName","true")
        trans.set("id", transition.name)
        trans.set("infiniteServer","false")
        trans.set("name",transition.name)
        trans.set("nameOffsetX","0")
        trans.set("nameOffsetY","0")
        trans.set("player","0")

        if constants.LAYOUT_INFORMATION_PETRI in transition.properties:
            trans.set("positionX", str(transition.properties[constants.LAYOUT_INFORMATION_PETRI][0][0]))
            trans.set("positionY", str(transition.properties[constants.LAYOUT_INFORMATION_PETRI][0][1]))
        else:
            trans.set("positionX", "0")
            trans.set("positionY", "0")
        trans.set("priority","0")
        trans.set("urgent","false")
        if constants.STOCHASTIC_DISTRIBUTION in transition.properties:
            random_variable = transition.properties[constants.STOCHASTIC_DISTRIBUTION]
            stochastic_information = etree.SubElement(trans, "toolspecific")
            stochastic_information.set("tool", "StochasticPetriNet")
            stochastic_information.set("version", "0.2")
            distribution_type = etree.SubElement(stochastic_information, "property")
            distribution_type.set("key", "distributionType")
            distribution_type.text = random_variable.get_distribution_type()
            if not random_variable.get_distribution_type() == "IMMEDIATE":
                distribution_parameters = etree.SubElement(stochastic_information, "property")
                distribution_parameters.set("key", "distributionParameters")
                distribution_parameters.text = random_variable.get_distribution_parameters()
            distribution_priority = etree.SubElement(stochastic_information, "property")
            distribution_priority.set("key", "priority")
            distribution_priority.text = str(random_variable.get_priority())
            distribution_invisible = etree.SubElement(stochastic_information, "property")
            distribution_invisible.set("key", "invisible")
            distribution_invisible.text = str(True if transition.label is None else False).lower()
            distribution_weight = etree.SubElement(stochastic_information, "property")
            distribution_weight.set("key", "weight")
            distribution_weight.text = str(random_variable.get_weight())
        # specific for data Petri nets
        if petri_properties.TRANS_GUARD in transition.properties:
            trans.set(petri_properties.TRANS_GUARD, transition.properties[petri_properties.TRANS_GUARD])
        if petri_properties.READ_VARIABLE in transition.properties:
            read_variables = transition.properties[petri_properties.READ_VARIABLE]
            for rv in read_variables:
                rv_el = etree.SubElement(trans, petri_properties.READ_VARIABLE)
                rv_el.text = rv
        if petri_properties.WRITE_VARIABLE in transition.properties:
            write_variables = transition.properties[petri_properties.WRITE_VARIABLE]
            for wv in write_variables:
                wv_el = etree.SubElement(trans, petri_properties.WRITE_VARIABLE)
                wv_el.text = wv
    arc_index = 0
    for arc in petrinet.arcs:
        arc_el = etree.SubElement(page, "arc")
        if petri_properties.ARCTYPE in arc.properties and arc.properties[petri_properties.ARCTYPE] == petri_properties.INHIBITOR_ARC:
            arc_el.set("id", f"I{arc_index}")#str(hash(arc)))
        else:
            arc_el.set("id", f"A{arc_index}")#str(hash(arc)))
        if type(arc.source) is PetriNet.Place:
            arc_el.set("inscription","[0,inf)")
            arc_el.set("nameOffsetX","0")
            arc_el.set("nameOffsetY","0")
            arc_el.set("source", str(places_map[arc.source]))
            arc_el.set("target", str(transitions_map[arc.target]))
            arc_el.set("type","timed")
        else:
            arc_el.set("inscription","1")
            arc_el.set("nameOffsetX","0")
            arc_el.set("nameOffsetY","0")
            arc_el.set("source", str(transitions_map[arc.source]))
            arc_el.set("target", str(places_map[arc.target]))
            arc_el.set("type","normal")

        if petri_properties.ARCTYPE in arc.properties:
            arc_type = arc.properties[petri_properties.ARCTYPE]
            if arc_type == petri_properties.INHIBITOR_ARC:
                arc_type = "tapnInhibitor"
                arc_el.set("inscription","[0,inf)")
            elif arc_type == petri_properties.TRANSPORT_ARC:
                age_min = "0"
                age_max = "inf"
                t_idx = "1"
                if petri_properties.AGE_MIN in arc.properties:
                    age_min = str(arc.properties[petri_properties.AGE_MIN])
                if petri_properties.AGE_MAX in arc.properties:
                    age_max = str(arc.properties[petri_properties.AGE_MAX])
                if petri_properties.TRANSPORT_INDEX in arc.properties:
                    t_idx = str(arc.properties[petri_properties.TRANSPORT_INDEX])
                inscription = f"[{age_min},{age_max}):{t_idx}"
                arc_el.set("inscription", inscription)
            arc_el.set("type", arc_type)

        if arc.weight > 1:
            arc_el.set("weight",str(arc.weight))
        else:
            arc_el.set("weight","1")

        for id in range(0,2):
            arc_path = etree.SubElement(arc_el, "arcpath")
            arc_path.set("arcPointType","false")
            arc_path.set("id",str(id))
            arc_path.set("xCoord","0")
            arc_path.set("yCoord","0")
        arc_index = arc_index + 1

    if len(final_marking) > 0:
        finalmarkings = etree.SubElement(net, "finalmarkings")
        marking = etree.SubElement(finalmarkings, "marking")

        for place in final_marking:
            placem = etree.SubElement(marking, "place")
            placem.set("idref", place.name)
            placem_text = etree.SubElement(placem, "text")
            placem_text.text = str(final_marking[place])

    # specific for data Petri nets
    if petri_properties.VARIABLES in petrinet.properties:
        variables = etree.SubElement(net, "variables")
        for prop in petrinet.properties[petri_properties.VARIABLES]:
            variable = etree.SubElement(variables, "variable")
            variable.set("type", prop["type"])
            variable_name = etree.SubElement(variable, "name")
            variable_name.text = prop["name"]

    k_bound = etree.SubElement(root,"k-bound")
    k_bound.set("bound","3")

    feature = etree.SubElement(root, "feature")
    feature.set("isGame", "false")
    if parameters and 'isTimed' in parameters:
        if parameters['isTimed']:
            feature.set("isTimed", "true")
        else:
            feature.set("isTimed", "false")
    else:
        feature.set("isTimed", "false")

    tree = etree.ElementTree(root)

    return tree

def export_petri_tree_old(petrinet, marking, final_marking=None, export_prom5=False, parameters=None):
    """
    Export a Petrinet to a XML tree

    Parameters
    ----------
    petrinet: :class:`pm4py.entities.petri.petrinet.PetriNet`
        Petri net
    marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Marking
    final_marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Final marking (optional)
    export_prom5
        Enables exporting PNML files in a format that is ProM5-friendly
    parameters
        Other parameters of the algorithm

    Returns
    ----------
    tree
        XML tree
    """
    if parameters is None:
        parameters = {}

    if final_marking is None:
        final_marking = Marking()

    root = etree.Element("pnml")
    net = etree.SubElement(root, "net")
    net.set("id", "net1")
    net.set("type", "http://www.pnml.org/version-2009/grammar/pnmlcoremodel")
    if export_prom5 is True:
        page = net
    else:
        page = etree.SubElement(net, "page")
        page.set("id", "n0")
    places_map = {}
    for place in petrinet.places:
        places_map[place] = place.name
        pl = etree.SubElement(page, "place")
        pl.set("id", place.name)
        pl_name = etree.SubElement(pl, "name")
        pl_name_text = etree.SubElement(pl_name, "text")
        pl_name_text.text = place.properties[
            constants.PLACE_NAME_TAG] if constants.PLACE_NAME_TAG in place.properties else place.name
        if place in marking:
            pl_initial_marking = etree.SubElement(pl, "initialMarking")
            pl_initial_marking_text = etree.SubElement(pl_initial_marking, "text")
            pl_initial_marking_text.text = str(marking[place])
        if constants.LAYOUT_INFORMATION_PETRI in place.properties:
            graphics = etree.SubElement(pl, "graphics")
            position = etree.SubElement(graphics, "position")
            position.set("x", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][0][0]))
            position.set("y", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][0][1]))
            dimension = etree.SubElement(graphics, "dimension")
            dimension.set("x", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][1][0]))
            dimension.set("y", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][1][1]))
    transitions_map = {}
    for transition in petrinet.transitions:
        transitions_map[transition] = transition.name
        trans = etree.SubElement(page, "transition")
        trans.set("id", transition.name)
        trans_name = etree.SubElement(trans, "name")
        trans_text = etree.SubElement(trans_name, "text")
        if constants.LAYOUT_INFORMATION_PETRI in transition.properties:
            graphics = etree.SubElement(trans, "graphics")
            position = etree.SubElement(graphics, "position")
            position.set("x", str(transition.properties[constants.LAYOUT_INFORMATION_PETRI][0][0]))
            position.set("y", str(transition.properties[constants.LAYOUT_INFORMATION_PETRI][0][1]))
            dimension = etree.SubElement(graphics, "dimension")
            dimension.set("x", str(transition.properties[constants.LAYOUT_INFORMATION_PETRI][1][0]))
            dimension.set("y", str(transition.properties[constants.LAYOUT_INFORMATION_PETRI][1][1]))
        if constants.STOCHASTIC_DISTRIBUTION in transition.properties:
            random_variable = transition.properties[constants.STOCHASTIC_DISTRIBUTION]
            stochastic_information = etree.SubElement(trans, "toolspecific")
            stochastic_information.set("tool", "StochasticPetriNet")
            stochastic_information.set("version", "0.2")
            distribution_type = etree.SubElement(stochastic_information, "property")
            distribution_type.set("key", "distributionType")
            distribution_type.text = random_variable.get_distribution_type()
            if not random_variable.get_distribution_type() == "IMMEDIATE":
                distribution_parameters = etree.SubElement(stochastic_information, "property")
                distribution_parameters.set("key", "distributionParameters")
                distribution_parameters.text = random_variable.get_distribution_parameters()
            distribution_priority = etree.SubElement(stochastic_information, "property")
            distribution_priority.set("key", "priority")
            distribution_priority.text = str(random_variable.get_priority())
            distribution_invisible = etree.SubElement(stochastic_information, "property")
            distribution_invisible.set("key", "invisible")
            distribution_invisible.text = str(True if transition.label is None else False).lower()
            distribution_weight = etree.SubElement(stochastic_information, "property")
            distribution_weight.set("key", "weight")
            distribution_weight.text = str(random_variable.get_weight())
        if transition.label is not None:
            trans_text.text = transition.label
        else:
            trans_text.text = transition.name
            tool_specific = etree.SubElement(trans, "toolspecific")
            tool_specific.set("tool", "ProM")
            tool_specific.set("version", "6.4")
            tool_specific.set("activity", "$invisible$")
            tool_specific.set("localNodeID", str(uuid.uuid4()))
        if export_prom5 is True:
            if transition.label is not None:
                prom5_specific = etree.SubElement(trans, "toolspecific")
                prom5_specific.set("tool", "ProM")
                prom5_specific.set("version", "5.2")
                log_event_prom5 = etree.SubElement(prom5_specific, "logevent")
                event_name = transition.label.split("+")[0]
                event_transition = transition.label.split("+")[1] if len(
                    transition.label.split("+")) > 1 else "complete"
                log_event_prom5_name = etree.SubElement(log_event_prom5, "name")
                log_event_prom5_name.text = event_name
                log_event_prom5_type = etree.SubElement(log_event_prom5, "type")
                log_event_prom5_type.text = event_transition
        # specific for data Petri nets
        if petri_properties.TRANS_GUARD in transition.properties:
            trans.set(petri_properties.TRANS_GUARD, transition.properties[petri_properties.TRANS_GUARD])
        if petri_properties.READ_VARIABLE in transition.properties:
            read_variables = transition.properties[petri_properties.READ_VARIABLE]
            for rv in read_variables:
                rv_el = etree.SubElement(trans, petri_properties.READ_VARIABLE)
                rv_el.text = rv
        if petri_properties.WRITE_VARIABLE in transition.properties:
            write_variables = transition.properties[petri_properties.WRITE_VARIABLE]
            for wv in write_variables:
                wv_el = etree.SubElement(trans, petri_properties.WRITE_VARIABLE)
                wv_el.text = wv
    for arc in petrinet.arcs:
        arc_el = etree.SubElement(page, "arc")
        arc_el.set("id", str(hash(arc)))
        if type(arc.source) is PetriNet.Place:
            arc_el.set("source", str(places_map[arc.source]))
            arc_el.set("target", str(transitions_map[arc.target]))
        else:
            arc_el.set("source", str(transitions_map[arc.source]))
            arc_el.set("target", str(places_map[arc.target]))

        if arc.weight > 1:
            inscription = etree.SubElement(arc_el, "inscription")
            arc_weight = etree.SubElement(inscription, "text")
            arc_weight.text = str(arc.weight)

        for prop_key in arc.properties:
            if prop_key == petri_properties.ARCTYPE:
                arc_type = arc.properties[petri_properties.ARCTYPE]
                arc_el.set("type",arc_type)
            else:
                element = etree.SubElement(arc_el, prop_key)
                element_text = etree.SubElement(element, "text")
                element_text.text = str(arc.properties[prop_key])

    if len(final_marking) > 0:
        finalmarkings = etree.SubElement(net, "finalmarkings")
        marking = etree.SubElement(finalmarkings, "marking")

        for place in final_marking:
            placem = etree.SubElement(marking, "place")
            placem.set("idref", place.name)
            placem_text = etree.SubElement(placem, "text")
            placem_text.text = str(final_marking[place])

    # specific for data Petri nets
    if petri_properties.VARIABLES in petrinet.properties:
        variables = etree.SubElement(net, "variables")
        for prop in petrinet.properties[petri_properties.VARIABLES]:
            variable = etree.SubElement(variables, "variable")
            variable.set("type", prop["type"])
            variable_name = etree.SubElement(variable, "name")
            variable_name.text = prop["name"]

    tree = etree.ElementTree(root)

    return tree


def export_petri_as_string(petrinet, marking, final_marking=None, export_prom5=False,
                           parameters=None):
    """
    Parameters
    ----------
    petrinet: :class:`pm4py.entities.petri.petrinet.PetriNet`
        Petri net
    marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Marking
    final_marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Final marking (optional)
    export_prom5
        Enables exporting PNML files in a format that is ProM5-friendly

    Returns
    ----------
    string
        Petri net as string
    """
    if parameters is None:
        parameters = {}

    # gets the XML tree
    tree = export_petri_tree(petrinet, marking, final_marking=final_marking,
                             export_prom5=export_prom5)

    # removing default decoding (return binary string as in other parts of the application)
    return etree.tostring(tree, xml_declaration=True, encoding=constants.DEFAULT_ENCODING)


def export_net(petrinet, marking, output_filename, final_marking=None, export_prom5=False,
               parameters=None):
    """
    Export a Petrinet to a PNML file

    Parameters
    ----------
    petrinet: :class:`pm4py.entities.petri.petrinet.PetriNet`
        Petri net
    marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Marking
    final_marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Final marking (optional)
    output_filename:
        Absolute output file name for saving the pnml file
    export_prom5
        Enables exporting PNML files in a format that is ProM5-friendly
    """
    if parameters is None:
        parameters = {}

    # gets the XML tree
    tree = export_petri_tree(petrinet, marking, final_marking=final_marking,
                             export_prom5=export_prom5)

    # write the tree to a file
    tree.write(output_filename, pretty_print=True, xml_declaration=True, encoding='utf-8')

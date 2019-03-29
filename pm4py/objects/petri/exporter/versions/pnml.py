import uuid

from lxml import etree

import pm4py
from pm4py.objects.petri.petrinet import Marking


def export_petri_tree(petrinet, marking, final_marking=None, stochastic_map=None, export_prom5=False, parameters=None):
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
    stochastic_map
        (only for stochastics) map that associates to each transition a probability distribution
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
        pl_name_text.text = place.name
        if place in marking:
            pl_initial_marking = etree.SubElement(pl, "initialMarking")
            pl_initial_marking_text = etree.SubElement(pl_initial_marking, "text")
            pl_initial_marking_text.text = str(marking[place])
    transitions_map = {}
    for transition in petrinet.transitions:
        transitions_map[transition] = transition.name
        trans = etree.SubElement(page, "transition")
        trans.set("id", transition.name)
        trans_name = etree.SubElement(trans, "name")
        trans_text = etree.SubElement(trans_name, "text")
        if stochastic_map is not None and transition in stochastic_map:
            random_variable = stochastic_map[transition]
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
    for arc in petrinet.arcs:
        arc_el = etree.SubElement(page, "arc")
        arc_el.set("id", str(hash(arc)))
        if type(arc.source) is pm4py.objects.petri.petrinet.PetriNet.Place:
            arc_el.set("source", str(places_map[arc.source]))
            arc_el.set("target", str(transitions_map[arc.target]))
        else:
            arc_el.set("source", str(transitions_map[arc.source]))
            arc_el.set("target", str(places_map[arc.target]))

    if len(final_marking) > 0:
        finalmarkings = etree.SubElement(net, "finalmarkings")
        marking = etree.SubElement(finalmarkings, "marking")

        for place in final_marking:
            placem = etree.SubElement(marking, "place")
            placem.set("idref", place.name)
            placem_text = etree.SubElement(placem, "text")
            placem_text.text = str(final_marking[place])
    tree = etree.ElementTree(root)

    return tree


def export_petri_as_string(petrinet, marking, final_marking=None, stochastic_map=None, export_prom5=False,
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
    stochastic_map
        (only for stochastics) map that associates to each transition a probability distribution
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
    tree = export_petri_tree(petrinet, marking, final_marking=final_marking, stochastic_map=stochastic_map,
                             export_prom5=export_prom5)

    return etree.tostring(tree, xml_declaration=True, encoding="utf-8")


def export_net(petrinet, marking, output_filename, final_marking=None, stochastic_map=None, export_prom5=False,
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
    stochastic_map
        (only for stochastics) map that associates to each transition a probability distribution
    export_prom5
        Enables exporting PNML files in a format that is ProM5-friendly
    """
    if parameters is None:
        parameters = {}

    # gets the XML tree
    tree = export_petri_tree(petrinet, marking, final_marking=final_marking, stochastic_map=stochastic_map,
                             export_prom5=export_prom5)

    # write the tree to a file
    tree.write(output_filename, pretty_print=True, xml_declaration=True, encoding="utf-8")

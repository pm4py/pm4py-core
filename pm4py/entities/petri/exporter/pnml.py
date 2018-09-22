from lxml import etree
import uuid
import pm4py
from pm4py.entities.petri.petrinet import Marking

def export_petri_tree(petrinet, marking, final_marking=None):
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

    Returns
    ----------
    tree
        XML tree
    """
    if final_marking is None:
        final_marking = Marking()

    root = etree.Element("pnml")
    net = etree.SubElement(root, "net")
    net.set("id","net1")
    net.set("type","http://www.pnml.org/version-2009/grammar/pnmlcoremodel")
    page = etree.SubElement(net, "page")
    page.set("id","n0")
    placesMap = {}
    for place in petrinet.places:
        placesMap[place] = place.name
        pl = etree.SubElement(page, "place")
        pl.set("id", place.name)
        plName = etree.SubElement(pl,"name")
        plNameText = etree.SubElement(plName,"text")
        plNameText.text = place.name
        if place in marking:
            plInitialMarking = etree.SubElement(pl,"initialMarking")
            plInitialMarkingText = etree.SubElement(plInitialMarking,"text")
            plInitialMarkingText.text = str(marking[place])
    transitionsMap = {}
    for transition in petrinet.transitions:
        transitionsMap[transition] = transition.name
        trans = etree.SubElement(page, "transition")
        trans.set("id", transition.name)
        transName = etree.SubElement(trans, "name")
        transText = etree.SubElement(transName, "text")
        if transition.label is not None:
            transText.text = transition.label
        else:
            transText.text = transition.name
            toolSpecific = etree.SubElement(trans, "toolspecific")
            toolSpecific.set("tool", "ProM")
            toolSpecific.set("version", "6.4")
            toolSpecific.set("activity", "$invisible$")
            toolSpecific.set("localNodeID", str(uuid.uuid4()))
    for arc in petrinet.arcs:
        arcEl = etree.SubElement(page, "arc")
        arcEl.set("id", str(hash(arc)))
        if type(arc.source) is pm4py.entities.petri.petrinet.PetriNet.Place:
            arcEl.set("source", str(placesMap[arc.source]))
            arcEl.set("target", str(transitionsMap[arc.target]))
        else:
            arcEl.set("source", str(transitionsMap[arc.source]))
            arcEl.set("target", str(placesMap[arc.target]))

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

def export_petri_as_string(petrinet, marking, final_marking=None):
    """
    Parameters
    ----------
    petrinet: :class:`pm4py.entities.petri.petrinet.PetriNet`
        Petri net
    marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Marking
    final_marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Final marking (optional)

    Returns
    ----------
    string
        Petri net as string
    """

    # gets the XML tree
    tree = export_petri_tree(petrinet, marking, final_marking=final_marking)

    return etree.tostring(tree, xml_declaration=True, encoding="utf-8")

def export_net(petrinet, marking, output_filename, final_marking=None):
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
    """

    # gets the XML tree
    tree = export_petri_tree(petrinet, marking, final_marking=final_marking)
    # write the tree to a file
    tree.write(output_filename, pretty_print=True, xml_declaration=True, encoding="utf-8")
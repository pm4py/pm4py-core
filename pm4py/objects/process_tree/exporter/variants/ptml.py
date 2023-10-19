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
import copy
import uuid

from lxml import etree

from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.process_tree.obj import Operator
from pm4py.util import constants, exec_utils
from enum import Enum


class Parameters(Enum):
    ENCODING = "encoding"


def get_list_nodes_from_tree(tree, parameters=None):
    """
    Gets the list of nodes from a process tree

    Parameters
    ---------------
    tree
        Process tree
    parameters
        Parameters

    Returns
    ---------------
    list_nodes
        List of nodes of the process tree
    """
    if parameters is None:
        parameters = {}

    list_nodes = []
    to_visit = [tree]

    while len(to_visit) > 0:
        node = to_visit.pop(0)
        for child in node.children:
            to_visit.append(child)
        list_nodes.append(node)

    return list_nodes


def export_ptree_tree(tree, parameters=None):
    """
    Exports the XML tree from a process tree

    Parameters
    -----------------
    tree
        Process tree
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    xml_tree
        XML tree object
    """
    tree = copy.deepcopy(tree)
    if parameters is None:
        parameters = {}

    nodes = get_list_nodes_from_tree(tree, parameters=parameters)
    nodes_dict = {(id(x), x): str(uuid.uuid4()) for x in nodes}

    # make sure that in the exporting, loops have 3 children
    # (for ProM compatibility)
    # just add a skip as third child
    for node in nodes:
        if node.operator == Operator.LOOP and len(node.children) < 3:
            third_children = ProcessTree(operator=None, label=None)
            third_children.parent = node
            node.children.append(third_children)
            nodes_dict[(id(third_children), third_children)] = str(uuid.uuid4())

    # repeat twice (structure has changed)
    nodes = get_list_nodes_from_tree(tree, parameters=parameters)
    nodes_dict = {(id(x), x): str(uuid.uuid4()) for x in nodes}

    root = etree.Element("ptml")
    processtree = etree.SubElement(root, "processTree")
    processtree.set("name", str(uuid.uuid4()))
    processtree.set("root", nodes_dict[(id(tree), tree)])
    processtree.set("id", str(uuid.uuid4()))

    for node in nodes:
        nk = nodes_dict[(id(node), node)]
        child = None
        if node.operator is None:
            if node.label is None:
                child = etree.SubElement(processtree, "automaticTask")
                child.set("name", "")
            else:
                child = etree.SubElement(processtree, "manualTask")
                child.set("name", node.label)
        else:
            if node.operator is Operator.SEQUENCE:
                child = etree.SubElement(processtree, "sequence")
            elif node.operator is Operator.XOR:
                child = etree.SubElement(processtree, "xor")
            elif node.operator is Operator.PARALLEL:
                child = etree.SubElement(processtree, "and")
            elif node.operator is Operator.OR:
                child = etree.SubElement(processtree, "or")
            elif node.operator is Operator.LOOP:
                child = etree.SubElement(processtree, "xorLoop")
            child.set("name", "")
        child.set("id", nk)

    for node in nodes:
        if not node == tree:
            child = etree.SubElement(processtree, "parentsNode")
            child.set("id", str(uuid.uuid4()))
            child.set("sourceId", nodes_dict[(id(node.parent), node.parent)])
            child.set("targetId", nodes_dict[(id(node), node)])

    tree = etree.ElementTree(root)
    return tree


def export_tree_as_string(tree, parameters=None):
    """
    Exports a process tree as a string

    Parameters
    ---------------
    tree
        Process tree
    parameters
        Parameters

    Returns
    ---------------
    stri
        XML string describing the process tree
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)

    # gets the XML tree
    tree = export_ptree_tree(tree, parameters=parameters)

    return etree.tostring(tree, xml_declaration=True, encoding=encoding)


def apply(tree, output_path, parameters=None):
    """
    Exports the process tree to a XML (.PTML) file

    Parameters
    ----------------
    tree
        Process tree
    output_path
        Output path
    parameters
        Parameters
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)

    # gets the XML tree
    tree = export_ptree_tree(tree, parameters=parameters)

    # exports the tree to a file
    F = open(output_path, "wb")
    tree.write(F, pretty_print=True, xml_declaration=True, encoding=encoding)
    F.close()

    return tree

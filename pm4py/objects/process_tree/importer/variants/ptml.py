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
import os
import tempfile

import deprecation
from lxml import etree, objectify

from pm4py import VERSION
from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.util import constants


@deprecation.deprecated(deprecated_in="2.1.1", removed_in="3.0",
                        current_version=VERSION,
                        details="Use the entrypoint import_from_string method")
def import_tree_from_string(tree_string, parameters=None):
    """
    Import a process tree from an XML string

    Parameters
    ----------
    tree_string
        Process tree expressed as PNML string
    parameters
        Other parameters of the algorithm

    Returns
    ----------
    tree
        Process tree
    """
    if parameters is None:
        parameters = {}

    fp = tempfile.NamedTemporaryFile(suffix='.ptml')
    fp.close()

    if type(tree_string) is bytes:
        with open(fp.name, 'wb') as f:
            f.write(tree_string)
    else:
        with open(fp.name, 'w') as f:
            f.write(tree_string)

    tree = apply(fp.name, parameters=parameters)
    os.remove(fp.name)
    return tree


def apply(path, parameters=None):
    """
    Imports a PTML file from the specified path

    Parameters
    ---------------
    path
        Path
    parameters
        Possible parameters

    Returns
    ---------------
    tree
        Process tree
    """
    if parameters is None:
        parameters = {}

    parser = etree.XMLParser(remove_comments=True)
    xml_tree = objectify.parse(path, parser=parser)
    root = xml_tree.getroot()

    return import_tree_from_xml_object(root, parameters=parameters)


def import_tree_from_string(tree_string, parameters=None):
    """
    Imports a PTML file from a (binary) string

    Parameters
    ---------------
    tree_string
        String representing the process tree
    parameters
        Possible parameters

    Returns
    ---------------
    tree
        Process tree
    """
    if parameters is None:
        parameters = {}

    if type(tree_string) is str:
        tree_string = tree_string.encode(constants.DEFAULT_ENCODING)

    parser = etree.XMLParser(remove_comments=True)
    root = objectify.fromstring(tree_string, parser=parser)

    return import_tree_from_xml_object(root, parameters=parameters)


def import_tree_from_xml_object(root, parameters=None):
    """
    Imports a process tree from the XML object

    Parameters
    ---------------
    root
        Root of the XML object
    parameters
        Possible parameters

    Returns
    ---------------
    tree
        Process tree
    """
    if parameters is None:
        parameters = {}

    nodes = {}

    for c0 in root:
        root = c0.get("root")
        for child in c0:
            tag = child.tag
            id = child.get("id")
            name = child.get("name")
            sourceId = child.get("sourceId")
            targetId = child.get("targetId")
            if name is not None:
                # node
                if tag == "and":
                    operator = Operator.PARALLEL
                    label = None
                elif tag == "sequence":
                    operator = Operator.SEQUENCE
                    label = None
                elif tag == "xor":
                    operator = Operator.XOR
                    label = None
                elif tag == "xorLoop":
                    operator = Operator.LOOP
                    label = None
                elif tag == "or":
                    operator = Operator.OR
                    label = None
                elif tag == "manualTask":
                    operator = None
                    label = name
                elif tag == "automaticTask":
                    operator = None
                    label = None
                else:
                    raise Exception("unknown tag: " + tag)
                tree = ProcessTree(operator=operator, label=label)
                nodes[id] = tree
            else:
                nodes[sourceId].children.append(nodes[targetId])
                nodes[targetId].parent = nodes[sourceId]

    # make sure that .PTML files having loops with 3 children are imported
    # into the PM4Py process tree structure
    # we want loops to have two children
    for node in nodes.values():
        if node.operator == Operator.LOOP and len(node.children) == 3:
            if not (node.children[2].operator is None and node.children[2].label is None):
                parent_node = node.parent
                new_parent_node = ProcessTree(operator=Operator.SEQUENCE, label=None)
                node.parent = new_parent_node
                new_parent_node.children.append(node)
                node.children[2].parent = new_parent_node
                new_parent_node.children.append(node.children[2])
                if parent_node is not None:
                    new_parent_node.parent = parent_node
                    del parent_node.children[parent_node.children.index(node)]
                    parent_node.children.append(new_parent_node)
            del node.children[2]

    return nodes[root]

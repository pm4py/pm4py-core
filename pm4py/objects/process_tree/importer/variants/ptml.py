from lxml import etree, objectify
from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.objects.process_tree.pt_operator import Operator
import tempfile
import os


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

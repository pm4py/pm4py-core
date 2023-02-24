import xml.etree.ElementTree as ET
from typing import Dict, Any, Tuple


def apply(file_name: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    tree = ET.parse(file_name)
    root = tree.getroot()
    nodes = {}
    edges = {}
    for child in root:
        for child2 in child:
            this_class = child2.get("class")
            if this_class in ["node", "edge"]:
                title = None
                label_x = None
                label_y = None
                label_text = None
                polygon = None
                for child3 in child2:
                    if child3.tag.endswith("title"):
                        title = child3.text
                    elif child3.tag.endswith("text"):
                        label_x = child3.get("x")
                        label_y = child3.get("y")
                        label_text = child3.text
                    elif child3.tag.endswith("polygon"):
                        polygon = child3.get("points").split(" ")
                        polygon = [x.split(",") for x in polygon]
                        polygon = tuple((float(x[0]), float(x[1])) for x in polygon)
                if this_class == "node":
                    nodes[title] = {"label": label_text, "label_x": label_x, "label_y": label_y, "polygon": polygon}
                elif this_class == "edge":
                    title = title.replace("->", " ").strip()
                    these_nodes = tuple(title.split(" "))
                    if these_nodes[0] in nodes and these_nodes[1] in nodes:
                        edges[these_nodes] = {"label": label_text, "label_x": label_x, "label_y": label_y,
                                              "polygon": polygon}

    return nodes, edges

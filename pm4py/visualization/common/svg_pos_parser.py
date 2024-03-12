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
            if this_class in ["cluster", "node", "edge"]:
                title = None
                label_x = None
                label_y = None
                label_text = None
                polygon = None
                waypoints = None
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
                    elif child3.tag.endswith("path"):
                        pa = child3.get("d").replace("C", " ")[1:]
                        waypoints = pa.split()
                        waypoints = [x.split(",") for x in waypoints]
                        waypoints = [(float(x[0]), float(x[1])) for x in waypoints]

                if this_class == "node" or this_class == "cluster":
                    key_name = title
                    if this_class == "cluster":
                        key_name = key_name.split(this_class)[-1]
                    nodes[key_name] = {"label": label_text, "label_x": label_x, "label_y": label_y, "polygon": polygon}
                elif this_class == "edge":
                    title = title.replace("-", " ").replace(">", " ").strip()
                    these_nodes = tuple(title.split(" "))
                    if these_nodes[0] in nodes and these_nodes[-1] in nodes:
                        edges[(these_nodes[0], these_nodes[-1])] = {"label": label_text, "label_x": label_x, "label_y": label_y,
                                              "polygon": polygon, "waypoints": waypoints}

    return nodes, edges

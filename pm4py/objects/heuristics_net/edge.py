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
class Edge:
    def __init__(self, start_node, end_node, dependency_value, dfg_value, repr_value, label="", repr_color="#000000",
                 edge_type="frequency", net_name=""):
        """
        Constructor

        Parameters
        ------------
        start_node
            Start node of the edge
        end_node
            End node of the edge
        dependency_value
            Dependency value of the edge
        dfg_value
            DFG value of the edge
        repr_value
            Value used in the representation
        label
            (If provided) label of the edge
        repr_color
            (If provided) Color that shall represent the edge
        edge_type
            Type of the edge (frequency or performance)
        net_name
            (If provided) name of the Heuristics Net
        """
        self.start_node = start_node
        self.end_node = end_node
        self.dependency_value = dependency_value
        self.dfg_value = dfg_value
        self.repr_value = repr_value
        self.label = label
        self.repr_color = repr_color
        self.edge_type = edge_type
        self.net_name = net_name
        self.repr_font_color = None
        self.pen_width = None

    def get_color(self):
        """
        Gets the color to use for the representation
        """
        return self.repr_color

    def get_font_color(self):
        """
        Gets the font color to use for the representation
        """
        if self.repr_font_color is not None:
            return self.repr_font_color
        return self.repr_color

    def get_penwidth(self, default):
        """
        Gets the pen width to use for the representation

        Parameters
        --------------
        default
            Default value
        """
        if self.pen_width is not None:
            return self.pen_width
        return default

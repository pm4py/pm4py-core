class Edge:
    def __init__(self, start_node, end_node, dependency_value, dfg_value, label="", repr_color="#000000"):
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
        label
            (If provided) label of the edge
        repr_color
            (If provided) Color that shall represent the edge
        """
        self.start_node = start_node
        self.end_node = end_node
        self.dependency_value = dependency_value
        self.dfg_value = dfg_value
        self.label = label
        self.repr_color = repr_color

from pm4py.objects.dcr.obj import DCR_Graph
from typing import Set, Dict
class RoleDCR_Graph(DCR_Graph):
    def __init__(self, g: DCR_Graph, template):
        self.__g = g
        self.__principals = template['principals']
        self.__roles = template['roles']
        self.__roleAssignments = template['roleAssignments']

    @property
    def principals(self) -> Set[str]:
        """
        principals(dict): A set representing the principals in the graph
        """
        return self.__principals

    @property
    def roles(self):
        """
        roles(dict): A set representing the principals in the graph
        """
        return self.__roles

    @property
    def roleAssignments(self):
        """
        roleAssignments(dict): A set representing the principals in the graph
        """
        return self.__roleAssignments

    def getConstraints(self):
        no = self.__g.getConstraints()
        for i in self.__roleAssignments.values():
            no += len(i)
        return no

    def __getattr__(self, name):
        return getattr(self.__g, name)

    def __getitem__(self, item):
        if hasattr(self.__g, item):
            return self.__g[item]
        for key, value in vars(self).items():
            if item == key.split("_")[-1]:
                return value


class nest_graph(object):
    def __init__(self, g, template):
        self.__g = g
        self.__nest = template['yo']

    def __getattr__(self, name):
        return getattr(self.__g, name)

    def __getitem__(self, item):
        if hasattr(self.__g, item):
            return self.__g[item]
        for key, value in vars(self).items():
            if item == key.split("_")[-1]:
                return value

from pm4py.objects.dcr.obj import DCR_Graph
from typing import Set


class RoleDCR_Graph(object):
    def __init__(self, g: DCR_Graph):
        self.__g = g
        self.__principals = set()
        self.__roles = set()
        self.__roleAssignments = {}
        self.__readRoleAssignments = {}

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

    @property
    def readRoleAssignments(self):
        """
        readRoleAssignments(dict): A set representing the principals in the graph
        """
        return self.__readRoleAssignments

    def getConstraints(self):
        """
        compute role assignments as constraints in DCR Graph

        Returns
        -------
        no
            number of constraints
        """
        no = self.__g.getConstraints()
        for i in self.__roleAssignments.values():
            no += len(i)
        return no

    def __repr__(self):
        string = str(self.__g)
        for key, value in vars(self).items():
            if value is self.__g:
                continue
            string += str(key.split("_")[-1])+": "+str(value)+"\n"
        return string

    def __getattr__(self, name):
        return getattr(self.__g, name)

    def __getitem__(self, item):
        if hasattr(self.__g, item):
            return self.__g[item]
        for key, value in vars(self).items():
            if item == key.split("_")[-1]:
                return value

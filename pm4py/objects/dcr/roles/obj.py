from typing import Set


class RoleDCR_Graph(object):
    def __init__(self, g, template=None):
        self.__g = g
        self.__principals = set() if None else template.pop("principals", set())
        self.__roles = set() if None else template.pop("roles", set())
        self.__roleAssignments = {} if None else template.pop("roleAssignments", set())
        self.__principalsAssignment = {} if None else template.pop("principalsAssignments", set())

    @property
    def principals(self) -> Set[str]:
        return self.__principals

    @property
    def roles(self):
        return self.__roles

    @property
    def roleAssignments(self):
        return self.__roleAssignments

    @property
    def readRoleAssignments(self):
        return self.__principalsAssignment

    def getConstraints(self):
        """
        compute role assignments as constraints in DCR Graph and the underlying graph

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

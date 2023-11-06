from typing import Set


class RoleDCR_Graph(object):
    """
    A class representing a Role-based DCR graph.

    This class wraps around a DCR graph structure, extending it with role-based features such as principals,
    roles, role assignments, and principals assignments. It provides an interface to integrate roles into the
    DCR model and to compute role-based constraints as part of the graph.

    Attributes
    ----------
    
    self.__g : DCRGraph
        The underlying DCR graph structure.
    self.__principals : Set[str]
        A set of principal identifiers within the graph.
    self.__roles : Set[str]
        A set of role identifiers within the graph.
    self.__roleAssignments : Dict[str, Set[str]]
        A dictionary where keys are activity identifiers and values are sets of roles assigned to those activities.
    self.__principalsAssignment : Dict[str, Set[str]]
        A dictionary where keys are activity identifiers and values are sets of principals assigned to those activities.

    Methods
    -------
    
    getConstraints() -> int:
        Computes the total number of constraints in the DCR graph, including those derived from role assignments.

    Parameters
    ----------
    
    g : DCRGraph
        The underlying DCR graph structure.
    template : dict, optional
        A template dictionary to initialize the roles and assignments from, if provided.

    Examples
    --------

    dcr_graph = DCRGraph(...)\n
    role_graph = RoleDCR_Graph(dcr_graph, template={\n
        "principals": {"principal1", "principal2"},\n
        "roles": {"role1", "role2"},\n
        "roleAssignments": {"role1": {"activity1"}},\n
        "principalsAssignments": {"role1": {"principal1"}}\n
    })\n

    \nAccess role-based attributes\n
    principals = role_graph.principals\n
    roles = role_graph.roles\n
    role_assignments = role_graph.roleAssignments\n
    principals_assignment = role_graph.principalsAssignment\n

    \nCompute the number of constraints\n
    total_constraints = role_graph.getConstraints()\n
    """
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

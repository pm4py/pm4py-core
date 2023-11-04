import pandas as pd
from typing import Optional, Any, Union, Dict, Set
import pm4py
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.dcr.roles.obj import RoleDCR_Graph
from pm4py.objects.dcr.roles.obj import DCR_Graph
from pm4py.objects.log.obj import EventLog


def apply(log, G, parameters) -> RoleDCR_Graph:
    """
    this method calls the role miner

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog` or :class: 'pandas.Dataframe'
        Event log to use in the role miner
    G
        Dcr graph to apply additional attributes to
    parameters
        Parameters of the algorithm, including:
            activity_key: :class:`str`, optional
            resource_key: :class:`str`, optional
            group_key: :class:`str`, optional

    Returns
    -------
    G: :class: `pm4py.objects.dcr.roles.obj.RoleDCR_Graph`
        A DCR graph containing principals, roles and role assignment
    """
    role_mine = Role_Mining()
    return role_mine.mine(log, G, parameters)


class Role_Mining:
    def role_assignment_role_to_acitivity(self, G, log: pd.DataFrame, activity_key: str,
                                          group_key: str, resource_key: str) -> None:
        """
        If log has defined roles, mine for role assignment using the a role identifier

        Parameters
        ----------
        G
            DCR graph
        log
            event log
        activity_key
            attribute to be used as activity identifier
        group_key
            attribute to be used as role identifier in dcr graphs
        """
        # turn this into a dict that can iterated over
        act_roles_couple = dict(log.groupby([group_key, activity_key]).size())
        for couple in act_roles_couple:
            G.roleAssignments[couple[0]] = G.roleAssignments[couple[0]].union({couple[1]})

        act_roles_couple = dict(log.groupby([group_key, resource_key]).size())
        for couple in act_roles_couple:
            G.readRoleAssignments[couple[0]] = G.readRoleAssignments[couple[0]].union({couple[1]})

    def role_assignment_resource_to_acitivity(self, G, log: pd.DataFrame, activity_key: str,
                                              resource_key: str) -> None:
        """
        if log has no role defined attribute such as org:group or similar defined,
        resource_key will then be role identifier, inspired by DCRgraphs.net

        Parameters
        ----------
        G
            DCR graph
        log
            event log
        activity_key
            attribute to be used as activity identifier
        resource_key
            attribute to be used as role identifier in dcr graphs
        """
        # turn this into a dict that can iterated over
        act_roles_couple = dict(log.groupby([resource_key, activity_key]).size())
        for couple in act_roles_couple:
            G.roleAssignments[couple[0]] = G.roleAssignments[couple[0]].union({couple[1]})


    def mine(self, log: Union[pd.DataFrame, EventLog], G: DCR_Graph, parameters: Optional[Dict[Any, Any]]):
        """
        Main role mine algorithm, will mine for principals and roles in a DCR graphs, and associated role assignment.
        determine principals, roles and roleAssignment through unique occurrences in log.

        Parameters
        ----------
        log
            Event log used for mining
        G
            DCR graph to append additional attributes
        parameters
            optional parameters used for role mining
        Returns
        -------
        RoleDCR_Graph(G, dcr)
            returns a :class:`pm4py.objects.dcr.roles.obj.RoleDCR_Graph` with organizational attributes
        """
        activity_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_ACTIVITY_KEY, parameters,
                                                  xes_constants.DEFAULT_NAME_KEY)
        resource_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_RESOURCE_KEY, parameters,
                                                  xes_constants.DEFAULT_RESOURCE_KEY)
        group_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_GROUP_KEY, parameters,
                                               xes_constants.DEFAULT_GROUP_KEY)

        if not isinstance(log, pd.DataFrame):
            log = pm4py.convert_to_dataframe(log)

        dcr = {'principals': set(), 'roles': set(), 'roleAssignments': {}, 'readRoleAssignments': {}}

        keys = set(log.keys())
        if (resource_key not in keys) and (group_key not in keys):
            return G

        G = RoleDCR_Graph(G)
        # load resources if provided
        if resource_key in keys:
            principals = set(log[resource_key].values)
            principals = set(filter(lambda x: x == x, principals))
            G.principals.update(principals)


        # if no resources are provided, map roles to activities
        if group_key in keys:
            roles = set(log[group_key].values)
            roles = set(filter(lambda x: x == x, roles))
            G.roles.update(roles)
            for i in G.roles:
                G.roleAssignments[i] = set()
                G.readRoleAssignments[i] = set()

        else:
            G.roles.update(G.principals)
            for i in G.roles:
                G.roleAssignments[i] = set()

        # if both roles and resources are provided
        if (resource_key in keys) and (group_key in keys):
            self.role_assignment_role_to_acitivity(G, log, activity_key, group_key, resource_key)
        # if resources are provided, but no roles
        elif (group_key not in keys) and (resource_key in keys):
            self.role_assignment_resource_to_acitivity(G, log, activity_key, resource_key)
        return G

import pandas as pd
from copy import deepcopy
from typing import Optional, Any, Union, Dict
import pm4py
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.dcr.roles.obj import RoleDCR_Graph
from pm4py.objects.dcr.obj import dcr_template
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
    role_mine = RoleMining()
    return role_mine.mine(log, G, parameters)


class RoleMining:
    """
    The RoleMining provides a simple algorithm to mine for organizational data of an event log for DCR graphs

    After initialization, user can call mine(log, G, parameters), which will return a DCR Graph with roles.

    Methods
    -------
    mine(log, G, parameters)
        calls the main mining function, extract roles and principals from the log and perform rol


    Notes
    ------
    * NaN values are disregarded, if event in log has event with both, it will not store NaN as a role assignment
    * readRoleAssignment is used as
    """
    def __init__(self):
        self.graph = {"roles": set(), "principals": set(), "roleAssignments": {}, "principalsAssignments": {}}

    def role_assignment_role_to_acitivity(self, log: pd.DataFrame, activity_key: str,
                                          group_key: str, resource_key: str) -> None:
        """
        If log has defined roles, mine for role assignment using the a role identifier

        Parameters
        ----------
        log
            event log
        activity_key
            attribute to be used as activity identifier
        group_key
            attribute to be used as role identifier
        resource_key
            attribute to be used as resource identifier
        """
        # turn this into a dict that can iterated over
        act_roles_couple = dict(log.groupby([group_key, activity_key]).size())
        for couple in act_roles_couple:
            self.graph['roleAssignments'][couple[0]] = self.graph['roleAssignments'][couple[0]].union({couple[1]})
        act_roles_couple = dict(log.groupby([group_key, resource_key]).size())
        for couple in act_roles_couple:
            self.graph['principalsAssignments'][couple[0]] = self.graph['principalsAssignments'][couple[0]].union({couple[1]})


    def mine(self, log: Union[pd.DataFrame, EventLog], G, parameters: Optional[Dict[Any, Any]]):
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

        keys = set(log.keys())
        if (resource_key not in keys) and (group_key not in keys):
            raise ValueError('input log does not contain attribute identifiers for resources or roles')

        # load resources if provided
        principals = set(log[resource_key].values)
        principals = set(filter(lambda x: x == x, principals))
        self.graph['principals'] = principals

        # if no resources are provided, map roles to activities
        roles = set(log[group_key].values)
        roles = set(filter(lambda x: x == x, roles))
        self.graph['roles'] = roles
        for i in self.graph['roles']:
            self.graph['roleAssignments'][i] = set()
            self.graph['principalsAssignments'][i] = set()

        self.role_assignment_role_to_acitivity(log, activity_key, group_key, resource_key)
        return RoleDCR_Graph(G, self.graph)

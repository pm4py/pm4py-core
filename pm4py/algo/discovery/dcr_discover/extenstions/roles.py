# if the same org:resource(s) are associated with the same events than this is a role.
# The role is associated to a group of (org:resources) and a subset of events (concept:name)
import pandas as pd

import pm4py
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.dcr.roles.obj import RoleDCR_Graph
from collections import Counter
def apply(log, G, parameters):
    role_mine = Role_Mining()
    return role_mine.mine(log, G, parameters)


class Role_Mining:
    def role_assignment_role_to_acitivity(self, dcr, log, activity_key, role_key, resource_key):
        # turn this into a dict that can iterated over
        act_roles_couple = dict(log.groupby([role_key, activity_key]).size())
        resource_roles_couple = dict(log.groupby([role_key, activity_key]).size())
        for couple1, couple2 in zip(act_roles_couple,resource_roles_couple):
            dcr['roleAssignments'][couple1[0]] = dcr['roleAssignments'][couple1[0]].union({couple1[1]})

    def role_assignment_resource_to_acitivity(self, dcr, log, activity_key, resource_key):
        # turn this into a dict that can iterated over
        act_roles_couple = dict(log.groupby([resource_key, activity_key]).size())
        for couple in act_roles_couple:
            dcr['roleAssignments'][couple[0]] = dcr['roleAssignments'][couple[0]].union({couple[1]})

    def mine(self, log, G, parameters):

        activity_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_ACTIVITY_KEY, parameters,
                                                  xes_constants.DEFAULT_NAME_KEY)
        resource_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_RESOURCE_KEY, parameters,
                                                  xes_constants.DEFAULT_RESOURCE_KEY)
        group_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_GROUP_KEY, parameters,
                                              xes_constants.DEFAULT_GROUP_KEY)

        if not isinstance(log,pd.DataFrame):
            log = pm4py.convert_to_dataframe(log)

        dcr = {'principals': set(), 'roles': set(), 'roleAssignments': {}}
        # check if there is organizational for resources performing an event
        # raises exception, if no resources of roles are provided
        keys = set(log.keys())

        if (resource_key not in keys) and (group_key not in keys):
            return dcr

        #load resources if provided
        if resource_key in keys:
            dcr['principals'] = set(pm4py.get_event_attribute_values(log,resource_key))

        #if no resources are provided, map roles to activities
        if group_key in keys:
            dcr['roles'] = set(pm4py.get_event_attribute_values(log,group_key))
            for i in dcr['roles']:
                dcr['roleAssignments'][i] = set()
        else:
            dcr['roles'] = dcr['principals']
            for i in dcr['roles']:
                dcr['roleAssignments'][i] = set()

        # if both roles and resources are provided
        if (resource_key in keys) and (group_key in keys):
            self.role_assignment_role_to_acitivity(dcr, log, activity_key, group_key)
        # if resources are provided, but no roles
        elif (group_key not in keys) and (resource_key in keys):
            self.role_assignment_resource_to_acitivity(dcr, log, activity_key, resource_key)

        return RoleDCR_Graph(G, dcr)

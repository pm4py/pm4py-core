# if the same org:resource(s) are associated with the same events than this is a role.
# The role is associated to a group of (org:resources) and a subset of events (concept:name)
import pm4py
from pm4py.util import exec_utils, constants, xes_constants
import pandas as pd
def apply(log, dcr, parameters):
    role_mine = Role_Mining()
    return role_mine.mine(log, dcr, parameters)


class Role_Mining:
    def find_roles_from_log(self, dcr, log, activity_key, role_key, resource_key):
        activities = pm4py.project_on_event_attribute(log, activity_key)
        resources = pm4py.project_on_event_attribute(log, resource_key)
        roles = pm4py.project_on_event_attribute(log, role_key)
        for i,j,k in zip(activities,resources,roles):
            for activity,resource,role in zip(i,j,k):
                # if resource is nan, the there is no role assignment
                if role == role:
                    dcr['roleAssignment'][role].add((resource, activity))

    def determine_roles_from_resource(self, dcr, log, activity_key, resource_key):
        roles = pm4py.discover_organizational_roles(log,activity_key=activity_key,resource_key=resource_key)
        for i in roles:
            for resource in set(i.originator_importance):
                dcr['roleAssignment'][resource] = dcr['roleAssignment'][resource].union(set(i.activities))


    def mine(self, log, dcr, parameters):

        activity_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_ACTIVITY_KEY, parameters,
                                                  xes_constants.DEFAULT_NAME_KEY)
        resource_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_RESOURCE_KEY, parameters,
                                                  xes_constants.DEFAULT_RESOURCE_KEY)
        role_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_ROLE_KEY, parameters,
                                              xes_constants.DEFAULT_ROLE_KEY)


        # check if there is organizational for resources performing an event
        dcr['principals'] = set()
        dcr['roles'] = set()
        dcr['roleAssignment'] = {}
        # raises exception, if no resources of roles are provided
        keys = pm4py.get_event_attributes(log)


        if (resource_key not in keys) and (role_key not in keys):
            return dcr

        #load resources if provided
        if resource_key in keys:
            dcr['principals'] = set(pm4py.get_event_attribute_values(log,resource_key))

        #if no resources are provided, map roles to activities
        if role_key in keys:
            dcr['roles'] = set(pm4py.get_event_attribute_values(log,role_key))
            for i in dcr['roles']:
                dcr['roleAssignment'][i] = set()
        else:
            dcr['roles'] = dcr['principals']
            for i in dcr['roles']:
                dcr['roleAssignment'][i] = set()

        # if both roles and resources are provided
        if (resource_key in keys) and (role_key in keys):
            self.find_roles_from_log(dcr, log, activity_key, role_key, resource_key)

        # if resources are provided, but no roles
        elif (role_key not in keys) and (resource_key in keys):
            self.determine_roles_from_resource(dcr, log, activity_key, resource_key)

        return dcr

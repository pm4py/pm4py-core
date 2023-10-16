# if the same org:resource(s) are associated with the same events than this is a role.
# The role is associated to a group of (org:resources) and a subset of events (concept:name)

from pm4py.util import exec_utils, constants, xes_constants

def apply(log, dcr, parameters):
    role_mine = Role_Mining()
    return role_mine.mine(log, dcr, parameters)


class Role_Mining:
    def find_roles_from_log(self, dcr, log, activity_key, role_key, resource_key):
        dcr['roles'] = set(log[role_key])
        # extracts the union of org:resource, org:role, and activity
        tuple_df = log[[role_key, resource_key, activity_key]].apply(tuple, axis=1).copy()
        # store tuple of org:resource and activity together with associated role as key
        for e in tuple_df:
            if e[0] not in dcr.__rolesAssignment:
                d = set()
                d.add(e[1:])
                dcr.__rolesAssignment[e[0]] = d
            else:
                dcr.__rolesAssignment[e[0]].add(e)

    def determine_roles_from_resource(self, dcr, log):
        roles = set()
        roleAssign = {}
        # we import the role miner, to perform this task
        from pm4py.algo.organizational_mining.roles.algorithm import apply as role_alg
        mined_roles = role_alg(log)
        for i in range(len(mined_roles)):
            role = "role" + str(i)
            roles.add(role)
            for act in mined_roles[i].activities:
                for res in mined_roles[i].originator_importance.keys():
                    if role not in roleAssign.keys():
                        roleAssign[role] = {(act, res)}
                    else:
                        roleAssign[role].add((act, res))
        dcr['roles'] = roles
        dcr['roleAssignment'] = roleAssign


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
        if (resource_key not in log.keys()) and (role_key not in log.keys()):
            raise Exception(
                "no resources or roles in event log, to allow for process of roles to event log"
            )

        #load resources if provided
        if resource_key in log.keys():
            dcr['principals'] = set(log[resource_key])

        #if no resources are provided, map roles to activities
        if (resource_key not in log.keys()) and (role_key in log.keys()):
            dcr['roles'] = set(log[role_key]).copy

        #if both roles and resources are provided
        elif (resource_key in log.keys()) and (role_key in log.keys()):
            self.find_roles_from_log(dcr, log, activity_key, role_key, resource_key)

        #if resources are provided, but no roles
        else:
            self.determine_roles_from_resource(dcr, log)
        return dcr

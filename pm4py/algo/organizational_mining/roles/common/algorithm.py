'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from collections import Counter
import numpy as np
from pm4py.util import exec_utils
from enum import Enum
from pm4py.util import constants
from pm4py.objects.org.roles.obj import Role
from typing import List


class Parameters(Enum):
    ROLES_THRESHOLD_PARAMETER = "roles_threshold_parameter"
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def get_sum_from_dictio_values(dictio, parameters=None):
    """
    Get the sum of a dictionary values

    Parameters
    -------------
    dictio
        Dictionary
    parameters
        Parameters of the algorithm

    Returns
    --------------
    sum_values
        Sum of the dictionary values
    """
    return np.sum(list(dictio.values()))


def normalize_role(role, parameters=None):
    """
    Normalize a role

    Parameters
    --------------
    role
        Originators of the role
    parameters
        Parameters of the algorithm

    Returns
    --------------
    normalized_role
        Normalized multiset of originators
    """
    sum_role = get_sum_from_dictio_values(role)

    new_role = {}

    for res in role:
        new_role[res] = role[res] / float(sum_role)

    return new_role


def find_multiset_intersection(role1, role2, normalize=False, parameters=None):
    """
    Finds the intersection of a multiset

    Parameters
    -------------
    role1
        First role originators
    role2
        Second role originators
    normalize
        Do the normalization of the roles
    parameters
        Parameters of the algorithm

    Returns
    --------------
    intersection
        Intersection of the multiset
    """
    intersection = {}

    if normalize:
        role1 = normalize_role(role1, parameters=parameters)
        role2 = normalize_role(role2, parameters=parameters)

    for res in role1:
        if res in role2:
            intersection[res] = min(role1[res], role2[res])

    return intersection


def find_multiset_union(role1, role2, normalize=False, parameters=None):
    """
    Finds the union of a multiset

    Parameters
    -------------
    role1
        First role originators
    role2
        Second role originators
    normalize
        Do the normalization of the roles
    parameters
        Parameters of the algorithm

    Returns
    --------------
    union
        Union of the multiset
    """
    union = {}

    if normalize:
        role1 = normalize_role(role1, parameters=parameters)
        role2 = normalize_role(role2, parameters=parameters)

    for res in role1:
        if res in role2:
            union[res] = max(role1[res], role2[res])
        else:
            union[res] = role1[res]

    for res in role2:
        if res not in role1:
            union[res] = role2[res]

    return union


def find_role_similarity(roles, i, j, parameters=None):
    """
    Calculate a number of similarity between different roles

    Parameters
    -------------
    roles
        List of roles
    i
        Index of the first role
    j
        Index of the second role
    parameters
        Parameters of the algorithm

    Returns
    --------------
    similarity
        Similarity measure
    """
    num = get_sum_from_dictio_values(
        find_multiset_intersection(roles[i][1], roles[j][1], normalize=True, parameters=parameters),
        parameters=parameters)
    den = get_sum_from_dictio_values(
        find_multiset_union(roles[i][1], roles[j][1], normalize=True, parameters=parameters), parameters=parameters)

    return num / den


def aggregate_roles_iteration(roles, parameters=None):
    """
    Single iteration of the roles aggregation algorithm

    Parameters
    --------------
    roles
        Roles
    parameters
        Parameters of the algorithm

    Returns
    --------------
    agg_roles
        (Partially aggregated) roles
    """
    threshold = exec_utils.get_param_value(Parameters.ROLES_THRESHOLD_PARAMETER, parameters, 0.65)

    sim = []

    for i in range(len(roles)):
        for j in range(i + 1, len(roles)):
            sim.append((i, j, roles[i][0], roles[j][0], -find_role_similarity(roles, i, j, parameters=parameters)))

    sim = sorted(sim, key=lambda x: (x[-1], constants.DEFAULT_VARIANT_SEP.join(x[-3]), constants.DEFAULT_VARIANT_SEP.join(x[-2])))

    found_feasible = False

    if sim:
        if -sim[0][-1] > threshold:
            set_act1 = roles[sim[0][0]][0]
            set_act2 = roles[sim[0][1]][0]
            set_res1 = roles[sim[0][0]][1]
            set_res2 = roles[sim[0][1]][1]

            total_set_act = sorted(list(set(set_act1).union(set(set_act2))))
            total_set_res = Counter(set_res1 + set_res2)

            del roles[sim[0][0]]
            del roles[sim[0][1] - 1]

            roles.append([total_set_act, total_set_res])

            roles = sorted(roles, key=lambda x: constants.DEFAULT_VARIANT_SEP.join(x[0]))

            found_feasible = True

    return roles, found_feasible


def aggregate_roles_algorithm(roles, parameters=None):
    """
    Algorithm to aggregate similar roles

    Parameters
    --------------
    roles
        Roles
    parameters
        Parameters of the algorithm

    Returns
    --------------
    agg_roles
        (Aggregated) roles
    """
    found_feasible = True
    while found_feasible:
        roles, found_feasible = aggregate_roles_iteration(roles, parameters=parameters)

    return roles


def get_initial_roles(res_act_couples, parameters=None):
    """
    Get the initial list of roles (each activity is a stand-alone role)

    Parameters
    -------------
    res_act_couples
        (resource, activity) couples along with the number of occurrences
    parameters
        Parameters of the algorithm

    Returns
    -------------
    roles
        List of roles (set of activities + multiset of resources)
    """
    if parameters is None:
        parameters = {}

    roles0 = {}

    for ra_couple in res_act_couples.keys():
        res = ra_couple[0]
        act = ra_couple[1]

        if act not in roles0:
            roles0[act] = Counter()
        if res not in roles0[act]:
            roles0[act][res] = res_act_couples[ra_couple]

    roles = []

    for act in roles0:
        roles.append([[act], roles0[act]])

    roles = sorted(roles, key=lambda x: (len(x[0]), len(x[1]), constants.DEFAULT_VARIANT_SEP.join(sorted(x[0]))), reverse=True)

    roles = aggregate_roles_algorithm(roles, parameters=parameters)

    roles = sorted(roles, key=lambda x: (len(x[0]), len(x[1]), constants.DEFAULT_VARIANT_SEP.join(sorted(x[0]))), reverse=True)

    return roles


def apply(res_act_couples, parameters=None) -> List[Role]:
    """
    Apply the roles detection, introduced by
    Burattin, Andrea, Alessandro Sperduti, and Marco Veluscek. "Business models enhancement through discovery of roles." 2013 IEEE Symposium on Computational Intelligence and Data Mining (CIDM). IEEE, 2013.

    Parameters
    -------------
    res_act_couples
        (resource, activity) couples along with the number of occurrences
    parameters
        Parameters of the algorithm

    Returns
    -------------
    roles
        List of roles (set of activities + multiset of resources)
    """
    if parameters is None:
        parameters = {}

    roles = get_initial_roles(res_act_couples, parameters=parameters)

    final_roles = []

    for r in roles:
        dictio = {x: int(y) for x, y in r[1].items()}
        final_roles.append(Role(r[0], dictio))

    return final_roles

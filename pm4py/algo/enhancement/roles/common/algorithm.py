from collections import Counter
import numpy as np

ROLES_THRESHOLD_PARAMETER = "roles_threshold_parameter"


def get_sum_from_dictio_values(dictio, parameters=None):
    return np.sum(list(dictio.values()))


def find_multiset_intersection(role1, role2, normalize=False, parameters=None):
    intersection = {}

    for res in role1:
        if res in role2:
            intersection[res] = min(role1[res], role2[res])

    return intersection


def find_multiset_union(role1, role2, normalize=False, parameters=None):
    union = {}

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
    num = get_sum_from_dictio_values(find_multiset_intersection(roles[i][1], roles[j][1]), normalize=True, parameters=parameters)
    den = get_sum_from_dictio_values(find_multiset_union(roles[i][1], roles[j][1]), normalize=True, parameters=parameters)

    return num / den


def aggregate_roles_iteration(roles, parameters=None):
    threshold = parameters[ROLES_THRESHOLD_PARAMETER]

    sim = []

    for i in range(len(roles)):
        for j in range(i + 1, len(roles)):
            sim.append((i, j, roles[i][0], roles[j][0], -find_role_similarity(roles, i, j, parameters=parameters)))

    sim = sorted(sim, key=lambda x: (x[-1], ",".join(x[-3]), ",".join(x[-2])))

    if sim:
        print(-sim[0][-1])
        if -sim[0][-1] > threshold:
            set_act1 = roles[sim[0][0]][0]
            set_act2 = roles[sim[0][1]][0]
            set_res1 = roles[sim[0][0]][1]
            set_res2 = roles[sim[0][1]][1]

            total_set_act = sorted(list(set(set_act1).union(set(set_act2))))
            total_set_res = Counter(set_res1 + set_res2)

            del roles[sim[0][0]]
            del roles[sim[0][1]-1]

            roles.append([total_set_act, total_set_res])

            roles = sorted(roles, key=lambda x: ",".join(x[0]))

    return roles


def get_initial_roles(res_act_couples, parameters=None):
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

    roles = sorted(roles, key=lambda x: ",".join(x[0]))

    roles = aggregate_roles_iteration(roles, parameters=parameters)

    return roles


def apply(res_act_couples, parameters=None):
    if parameters is None:
        parameters = {}

    roles = get_initial_roles(res_act_couples, parameters=parameters)

    final_roles = []

    for r in roles:
        dictio = {x: int(y) for x, y in r[1].items()}
        final_roles.append([r[0], dictio])

    return final_roles

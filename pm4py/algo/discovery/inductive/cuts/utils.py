def merge_groups_based_on_activities(a, b, groups):
    group_a = None
    group_b = None
    for group in groups:
        if a in group:
            group_a = group
        if b in group:
            group_b = group
    groups = [group for group in groups if group != group_a and group != group_b]
    groups.append(group_a.union(group_b))
    return groups


def merge_lists_based_on_activities(a, b, groups):
    group_a = []
    group_b = []
    for group in groups:
        if a in group:
            group_a = group
        if b in group:
            group_b = group
    if group_a is group_b:
        return groups
    groups = [group for group in groups if group != group_a and group != group_b]
    groups.append(group_a + group_b)
    return groups

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

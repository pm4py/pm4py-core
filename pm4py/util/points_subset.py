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
def pick_chosen_points(m, n):
    """
    Pick chosen points in a list

    Parameters
    ------------
    m
        Number of wanted points
    n
        Number of current points

    Returns
    ------------
    indexes
        Indexes of chosen points
    """
    return [i * n // m + n // (2 * m) for i in range(m)]


def pick_chosen_points_list(m, lst):
    """
    Pick a chosen number of points from a list

    Parameters
    -------------
    m
        Number of wanted points
    lst
        List

    Returns
    -------------
    reduced_lst
        Reduced list
    """
    n = len(lst)
    points = pick_chosen_points(m, n)

    ret = []
    for i in points:
        ret.append(lst[i])

    return ret

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
def get_sorted_end_activities_list(end_activities):
    """
    Gets sorted end attributes list

    Parameters
    ----------
    end_activities
        Dictionary of end attributes associated with their count

    Returns
    ----------
    listact
        Sorted end attributes list
    """
    listact = []
    for ea in end_activities:
        listact.append([ea, end_activities[ea]])
    listact = sorted(listact, key=lambda x: x[1], reverse=True)
    return listact


def get_end_activities_threshold(ealist, decreasing_factor):
    """
    Get end attributes cutting threshold

    Parameters
    ----------
    ealist
        Sorted end attributes list
    decreasing_factor
        Decreasing factor of the algorithm

    Returns
    ---------
    threshold
        End attributes cutting threshold
    """

    threshold = ealist[0][1]
    for i in range(1, len(ealist)):
        value = ealist[i][1]
        if value > threshold * decreasing_factor:
            threshold = value
    return threshold

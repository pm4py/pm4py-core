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
import stringdist


def levenshtein(stru1, stru2):
    """
    Measures the Levenshtein distance between two strings

    Parameters
    ---------------
    stru1
        First string
    stru2
        Second string

    Returns
    ---------------
    levens_dist
        Levenshtein distance
    """
    return stringdist.levenshtein(stru1, stru2)

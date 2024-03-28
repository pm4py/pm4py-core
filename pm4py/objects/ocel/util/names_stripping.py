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

import re


match = re.compile(r'[^0-9a-zA-Z]+')


def apply(X: str, max_len: int = 100) -> str:
    X = X.split(" ")
    i = 0
    while i < len(X):
        X[i] = X[i].capitalize()
        i = i + 1
    X = "".join(X)
    stru = match.sub('', X).strip()
    if len(stru) > max_len:
        stru = stru[:100]
    return stru

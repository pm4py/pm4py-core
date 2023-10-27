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
def translate_infix_to_regex(infix):
    regex = "^"
    for i, act in enumerate(infix):
        is_last_activity = i == (len(infix) - 1)
        if act == "...":
            if is_last_activity:
                regex = f"{regex[:-1]}(,[^,]*)*"
            else:
                regex = f"{regex}([^,]*,)*"
        else:
            if is_last_activity:
                regex = f"{regex}{act}"
            else:
                regex = f"{regex}{act},"

    regex = f"{regex}$"
    return regex

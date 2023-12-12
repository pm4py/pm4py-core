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


ref_stri_1 = "ordabcchr"
ref_stri_2 = "ordabc"

re1 = re.compile(r"([^a-zA-Z0-9]+)")
re2 = re.compile(ref_stri_1)


def mask_non_alphanumeric(stri):
    stri_split = re1.split(stri)
    ret = []
    for el in stri_split:
        for char in el:
            if char.isalnum() or char == " " or char in ["(", ")", "*", ".", ",", "'", "\"", "=", "<", ">", "_", "+",
                                                         "-", "!"]:
                ret.append(char)
            else:
                ret.append(ref_stri_1 + ref_stri_2 + str(ord(char)) + ref_stri_1)
    return "".join(ret)


def restore_non_alphanumeric(stri):
    stri_split = re2.split(stri)
    ret = []
    for el in stri_split:
        if el.startswith(ref_stri_2):
            ret.append(chr(int(el[len(ref_stri_2):])))
        else:
            ret.append(el)
    return "".join(ret)

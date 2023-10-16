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
def get_new_char(label, shared_obj):
    """
    Get a new single character describing the activity, for the regex

    Parameters
    ------------
    label
        Label of the transition
    shared_obj
        Shared object
    """
    list_to_avoid = ["[", "]", "(", ")", "*", "+", "^", "?", "\r", "\n", " ", "\t", "$", "\"", "!", "#", "&", "%", "|",
                     ".", ",", ";", "-", "'", "\\", "/", "{", "}", "$"]
    shared_obj.count_char = shared_obj.count_char + 1
    while chr(shared_obj.count_char) in list_to_avoid:
        shared_obj.count_char = shared_obj.count_char + 1
    shared_obj.mapping_dictio[label] = chr(shared_obj.count_char)


class SharedObj:
    def __init__(self):
        self.mapping_dictio = None
        if self.mapping_dictio is None:
            self.mapping_dictio = {}
        self.count_char = 0

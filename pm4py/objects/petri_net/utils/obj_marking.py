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
import random


class ObjMarking(dict):
    def __init__(self, *args, **kwargs):
        self.picked_items = set()
        self.update(*args, **kwargs)

    def __getitem_original__(self, key):
        if key in self:
            return dict.__getitem__(self, key)
        return {}

    def __getitem__(self, key):
        return ObjMarkingAccessor(self, key)

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v


class ObjMarkingAccessor(object):
    def __init__(self, obj_marking, key):
        self.obj_marking = obj_marking
        self.key = key

    def __sub__(self, other):
        if isinstance(other, int):
            picked_items = set(random.sample(self.obj_marking.__getitem_original__(self.key), min(len(self.obj_marking.__getitem_original__(self.key)), other)))
            self.obj_marking.picked_items = picked_items
            diff = self.obj_marking.__getitem_original__(self.key).difference(picked_items)
            return diff
        else:
            diff = self.obj_marking.__getitem_original__(self.key).difference(other)
            return diff

    def __add__(self, other):
        if isinstance(other, int):
            picked_items = set(random.sample(self.obj_marking.picked_items, other))
            if self.key not in self.obj_marking:
                self.obj_marking[self.key] = set()
            new_value = self.obj_marking.__getitem_original__(self.key).union(picked_items)
            self.obj_marking[self.key] = new_value
            return new_value
        else:
            new_value = self.obj_marking.__getitem_original__(self.key).union(other)
            self.obj_marking[self.key] = new_value
            return new_value

    def __repr__(self):
        return str(self.obj_marking.__getitem_original__(self.key))

    def __str__(self):
        return str(self.obj_marking.__getitem_original__(self.key))

    def __lt__(self, other):
        if isinstance(other, int):
            if len(self.obj_marking.__getitem_original__(self.key)) < other:
                return True
            return False

    def __le__(self, other):
        if isinstance(other, int):
            if len(self.obj_marking.__getitem_original__(self.key)) <= other:
                return True
            return False

    def __gt__(self, other):
        if isinstance(other, int):
            if len(self.obj_marking.__getitem_original__(self.key)) > other:
                return True
            return False

    def __ge__(self, other):
        if isinstance(other, int):
            if len(self.obj_marking.__getitem_original__(self.key)) >= other:
                return True
            return False

    def __lt__(self, other):
        if isinstance(other, int):
            if len(self.obj_marking.__getitem_original__(self.key)) < other:
                return True
            return False

    def __eq__(self, other):
        if isinstance(other, int):
            if len(self.obj_marking.__getitem_original__(self.key)) <= other:
                return True
            return False
        else:
            return self.__dict__ == other.__dict__

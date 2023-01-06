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

import deprecation

class Semantics(object):
    @deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed, use PetriNetSemantics.is_enabled() instead")
    def is_enabled(self, t, pn, m, **kwargs):
        pass

    @deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed, use PetriNetSemantics.fire() instead")
    def execute(self, t, pn, m, **kwargs):
        pass

    @deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed, use PetriNetSemantics.fire() instead")
    def weak_execute(self, t, pn, m, **kwargs):
        pass

    @deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed")
    def enabled_transitions(self, pn, m, **kwargs):
        pass

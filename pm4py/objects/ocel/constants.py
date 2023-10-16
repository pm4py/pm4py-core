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
PARAM_EVENT_ID = "param:event:id"
PARAM_EVENT_ACTIVITY = "param:event:activity"
PARAM_EVENT_TIMESTAMP = "param:event:timestamp"
PARAM_OBJECT_ID = "param:object:id"
PARAM_OBJECT_TYPE = "param:object:type"
PARAM_OBJECT_TYPE_PREFIX_EXTENDED = "param:object:type:prefix:extended"
PARAM_QUALIFIER = "param:qualifier"
PARAM_CHNGD_FIELD = "param:chngfield"

DEFAULT_EVENT_ID = "ocel:eid"
DEFAULT_EVENT_ACTIVITY = "ocel:activity"
DEFAULT_EVENT_TIMESTAMP = "ocel:timestamp"
DEFAULT_OBJECT_ID = "ocel:oid"
DEFAULT_OBJECT_TYPE = "ocel:type"
DEFAULT_OBJECT_TYPE_PREFIX_EXTENDED = "ocel:type:"
DEFAULT_QUALIFIER = "ocel:qualifier"
DEFAULT_CHNGD_FIELD = "ocel:field"

OCEL_PREFIX = "ocel:"
OCEL_EVENTS_KEY = "ocel:events"
OCEL_OBJECTS_KEY = "ocel:objects"
OCEL_ID_KEY = "ocel:id"
OCEL_OMAP_KEY = "ocel:omap"
OCEL_TYPED_OMAP_KEY = "ocel:typedOmap"
OCEL_VMAP_KEY = "ocel:vmap"
OCEL_OVMAP_KEY = "ocel:ovmap"
OCEL_O2O_KEY = "ocel:o2o"
OCEL_OBJCHANGES_KEY = "ocel:objectChanges"
OCEL_EVTYPES_KEY = "ocel:eventTypes"
OCEL_OBJTYPES_KEY = "ocel:objectTypes"
OCEL_GLOBAL_LOG = "ocel:global-log"
OCEL_GLOBAL_LOG_ATTRIBUTE_NAMES = "ocel:attribute-names"
OCEL_GLOBAL_LOG_OBJECT_TYPES = "ocel:object-types"
OCEL_GLOBAL_LOG_VERSION = "ocel:version"
OCEL_GLOBAL_LOG_ORDERING = "ocel:ordering"
OCEL_GLOBAL_EVENT = "ocel:global-event"
OCEL_GLOBAL_OBJECT = "ocel:global-object"

PARAM_INTERNAL_INDEX = "param:internal:index"
DEFAULT_INTERNAL_INDEX = "@@index"

DEFAULT_GLOBAL_EVENT = {"ocel:activity": "__INVALID__"}
DEFAULT_GLOBAL_OBJECT = {"ocel:type": "__INVALID__"}
DEFAULT_ORDERING = "timestamp"
CURRENT_VERSION = "1.0"

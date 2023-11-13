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
from pm4py.util import exec_utils
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.objects.ocel.util import filtering_utils
from pm4py.objects.ocel.util import ocel_consistency
from pm4py.objects.ocel.importer.jsonocel.variants import classic
from pm4py.util import constants as pm4_constants
from enum import Enum
import json


class Parameters(Enum):
    ENCODING = "encoding"


def apply(file_path: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Imports an OCEL from a JSON-OCEL 2 standard file

    Parameters
    --------------
    file_path
        Path to the object-centric event log
    parameters
        Possible parameters of the method, including:
        - Parameters.ENCODING

    Returns
    -------------
    ocel
        Object-centric event log
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, pm4_constants.DEFAULT_ENCODING)

    F = open(file_path, "r", encoding=encoding)
    json_obj = json.load(F)
    F.close()

    legacy_obj = {}
    legacy_obj["ocel:events"] = {}
    legacy_obj["ocel:objects"] = {}
    legacy_obj["ocel:objectChanges"] = []

    for eve in json_obj["events"]:
        dct = {}
        dct["ocel:activity"] = eve["type"]
        dct["ocel:timestamp"] = eve["time"]
        dct["ocel:vmap"] = {}
        if "attributes" in eve and eve["attributes"]:
            dct["ocel:vmap"] = {x["name"]: x["value"] for x in eve["attributes"]}
        dct["ocel:typedOmap"] = []
        if "relationships" in eve and eve["relationships"]:
            dct["ocel:typedOmap"] = [{"ocel:oid": x["objectId"], "ocel:qualifier": x["qualifier"]} for x in eve["relationships"]]
        dct["ocel:omap"] = list(set(x["ocel:oid"] for x in dct["ocel:typedOmap"]))
        legacy_obj["ocel:events"][eve["id"]] = dct

    for obj in json_obj["objects"]:
        dct = {}
        dct["ocel:type"] = obj["type"]
        dct["ocel:ovmap"] = {}
        if "attributes" in obj and obj["attributes"]:
            for x in obj["attributes"]:
                if x["name"] in dct["ocel:ovmap"]:
                    legacy_obj["ocel:objectChanges"].append({"ocel:oid": obj["id"], "ocel:type": obj["type"], "ocel:field": x["name"], x["name"]: x["value"], "ocel:timestamp": x["time"]})
                else:
                    dct["ocel:ovmap"][x["name"]] = x["value"]
        dct["ocel:o2o"] = []
        if "relationships" in obj and obj["relationships"]:
            dct["ocel:o2o"] = [{"ocel:oid": x["objectId"], "ocel:qualifier": x["qualifier"]} for x in obj["relationships"]]
        legacy_obj["ocel:objects"][obj["id"]] = dct

    legacy_obj["ocel:global-log"] = {}
    legacy_obj["ocel:global-event"] = {}
    legacy_obj["ocel:global-object"] = {}

    log = classic.get_base_ocel(legacy_obj, parameters=parameters)

    log = ocel_consistency.apply(log, parameters=parameters)
    log = filtering_utils.propagate_relations_filtering(log, parameters=parameters)

    return log

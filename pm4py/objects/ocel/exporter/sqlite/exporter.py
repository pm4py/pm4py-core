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

from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel.exporter.sqlite.variants import pandas_exporter, ocel20
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


class Variants(Enum):
    PANDAS_EXPORTER = pandas_exporter
    OCEL20 = ocel20


def apply(ocel: OCEL, target_path: str, variant=Variants.PANDAS_EXPORTER, parameters: Optional[Dict[Any, Any]] = None):
    """
    Exports an OCEL to a SQLite database

    Parameters
    -------------
    ocel
        Object-centric event log
    target_path
        Path to the SQLite database
    variant
        Variant to use. Possible values:
        - Variants.PANDAS_EXPORTER => Pandas exporter
    parameters
        Variant-specific parameters
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(ocel, target_path, parameters=parameters)

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

from pm4py.objects.ocel.obj import OCEL
from typing import Dict, Any
from enum import Enum
from typing import Optional
from pm4py.objects.ocel.importer.sqlite.variants import pandas_importer, ocel20
from pm4py.util import exec_utils


class Variants(Enum):
    PANDAS_IMPORTER = pandas_importer
    OCEL20 = ocel20


def apply(file_path: str, variant=Variants.PANDAS_IMPORTER, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Imports an OCEL from a SQLite database

    Parameters
    --------------
    file_path
        Path to the SQLite database
    variant
        Variant of the importer to use:
        - Variants.PANDAS_IMPORTER => Pandas
    parameters
        Variant-specific parameters

    Returns
    --------------
    ocel
        Object-centric event log
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(file_path, parameters=parameters)

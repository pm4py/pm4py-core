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
from pm4py.visualization.sna.variants import networkx, pyvis
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.org.sna.obj import SNA


class Variants(Enum):
    NETWORKX = networkx
    PYVIS = pyvis


DEFAULT_VARIANT = Variants.NETWORKX


def apply(metric_values: SNA, parameters=None, variant=DEFAULT_VARIANT):
    """
    Perform SNA visualization starting from the Matrix Container object
    and the Resource-Resource matrix

    Parameters
    -------------
    metric_values
        Value of the metrics
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm to use, possible values:
            - Variants.NETWORKX
            - Variants.PYVIS

    Returns
    -------------
    temp_file_name
        Name of a temporary file where the visualization is placed
    """
    return exec_utils.get_variant(variant).apply(metric_values, parameters=parameters)


def view(temp_file_name, parameters=None, variant=DEFAULT_VARIANT):
    """
    View the SNA visualization on the screen

    Parameters
    -------------
    temp_file_name
        Temporary file name
    parameters
        Possible parameters of the algorithm
    """
    return exec_utils.get_variant(variant).view(temp_file_name, parameters=parameters)


def save(temp_file_name, dest_file, parameters=None, variant=DEFAULT_VARIANT):
    """
    Save the SNA visualization from a temporary file to a well-defined destination file

    Parameters
    -------------
    temp_file_name
        Temporary file name
    dest_file
        Destination file
    parameters
        Possible parameters of the algorithm
    """
    return exec_utils.get_variant(variant).save(temp_file_name, dest_file, parameters=parameters)

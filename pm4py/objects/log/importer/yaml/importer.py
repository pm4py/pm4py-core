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
import yaml
from pm4py.util import constants
from pm4py.objects.log.importer.yaml.variants import yaml_loader
from pm4py.objects.log.importer.yaml.variants.yaml_loader import LoaderType

DEFAULT_VARIANT = LoaderType.C_SAFE_PYYAML


def apply(
    path,
    parameters=None,
    variant=DEFAULT_VARIANT,
):
    """
    Import a XES-YAML log into a EventLog object

    Parameters
    -----------
    path
        Log path
    parameters
        Parameters of the algorithm, including
            Parameters.TIMESTAMP_SORT -> Specify if we should sort log by timestamp
            Parameters.TIMESTAMP_KEY -> If sort is enabled, then sort the log by using this key
            Parameters.REVERSE_SORT -> Specify in which direction the log should be sorted
            Parameters.INSERT_TRACE_INDICES -> Specify if trace indexes should be added as event attribute for each event
            Parameters.MAX_TRACES -> Specify the maximum number of traces to import from the log (read in order in the YAML file)
    variant
        Variant of the algorithm to use, including:
            - Variants.ITERPARSE
            - Variants.LINE_BY_LINE

    Returns
    -----------
    log
        Trace log object
    """

    return yaml_loader.apply(path, parameters=parameters, variant=variant)


def get_log_header(
    path: str,
    variant=DEFAULT_VARIANT,
    encoding: str = constants.DEFAULT_ENCODING,
):
    """
    Returns the header of the log file

    Parameters
    -----------
    path
        Log path

    Returns
    -----------
    log
        Log header (first document of the XES-YAML event log)
    """

    yaml_loader = yaml.SafeLoader
    if variant == "safe":
        yaml_loader = yaml.SafeLoader
    elif variant == "full":
        yaml_loader = yaml.FullLoader

    with open(path, "r", encoding=encoding) as yaml_file:
        yaml_doc_stream = yaml.load_all(stream=yaml_file, Loader=yaml_loader)
        for document in yaml_doc_stream:
            if "log" in document.keys():
                return document

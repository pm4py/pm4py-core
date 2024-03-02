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
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.log.exporter.yaml.variants import yaml_dumper
from pm4py.objects.log.exporter.yaml.variants.yaml_dumper import DumperType
from pm4py.util import exec_utils


DEFAULT_VARIANT = DumperType.C_DUMPER


def apply(
    log,
    output_file_path,
    variant=DEFAULT_VARIANT,
    parameters=None,
    append=False,
    log_header=None,
):
    """
    Method to export a XES-YAML from a log

    Parameters
    -----------
    log
        Trace log
    output_file_path
        Output file path
    variant
        Selected variant of the algorithm
    parameters
        Parameters of the algorithm:
            Parameters.COMPRESS -> Indicates that the XES-YAML file must be compressed
    """

    parameters = dict() if parameters is None else parameters

    yaml_dumper.apply(
        log_conversion.apply(
            log, variant=log_conversion.Variants.TO_EVENT_LOG, parameters=parameters
        ),
        output_file_path,
        variant,
        parameters=parameters,
        append=append,
        log_header=log_header,
    )


def serialize(log, variant=DEFAULT_VARIANT, parameters=None):
    """
    Serialize a log into a binary string containing the XES of the log

    Parameters
    -----------
    log
        Trace log
    variant
        Selected variant of the algorithm
    parameters
        Parameters of the algorithm

    Returns
    -----------
    string
        String describing the XES
    """
    parameters = dict() if parameters is None else parameters

    log_string = exec_utils.get_variant(variant).export_log_as_string(
        log_conversion.apply(
            log, variant=log_conversion.Variants.TO_EVENT_LOG, parameters=parameters
        ),
        parameters=parameters,
    )

    return log_string

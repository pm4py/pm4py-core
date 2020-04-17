import deprecation

from pm4py.objects.petri.importer.versions import pnml

PNML = "pnml"

VERSIONS = {PNML: pnml.import_net}

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use importer module instead.')
def apply(input_file_path, variant=PNML, parameters=None):
    """
    Import a Petri net from a PNML file

    Parameters
    ------------
    input_file_path
        Input file path
    parameters
        Other parameters of the importer
    """
    return VERSIONS[variant](input_file_path, parameters=parameters)

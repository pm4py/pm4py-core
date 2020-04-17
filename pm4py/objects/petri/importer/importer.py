from pm4py.objects.petri.importer.versions import pnml

PNML = "pnml"

VERSIONS = {PNML: pnml.import_net}


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

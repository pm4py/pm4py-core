from pm4py.objects.petri.exporter.versions import pnml

PNML = "pnml"

VERSIONS = {PNML: pnml.export_net}


def apply(net, initial_marking, output_filename, final_marking=None, variant=PNML, parameters=None):
    """
    Export a Petri net along with an initial marking (and possibly a final marking) to an output file

    Parameters
    ------------
    net
        Petri net
    initial_marking
        Initial marking
    output_filename
        Output filename
    final_marking
        Final marking
    variant
        Variant of the algorithm, possible values: pnml
    parameters
        Parameters of the exporter
    """
    return VERSIONS[variant](net, initial_marking, output_filename, final_marking=final_marking, parameters=parameters)

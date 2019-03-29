import functools
import warnings

from pm4py.objects.petri.exporter import versions


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func


@deprecated
def export_petri_tree(petrinet, marking, final_marking=None, stochastic_map=None, export_prom5=False):
    """
    Export a Petrinet to a XML tree

    Parameters
    ----------
    petrinet: :class:`pm4py.entities.petri.petrinet.PetriNet`
        Petri net
    marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Marking
    final_marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Final marking (optional)
    stochastic_map
        (only for stochastics) map that associates to each transition a probability distribution
    export_prom5
        Enables exporting PNML files in a format that is ProM5-friendly

    Returns
    ----------
    tree
        XML tree
    """
    return versions.pnml.export_petri_tree(petrinet, marking, final_marking=final_marking,
                                           stochastic_map=stochastic_map, export_prom5=export_prom5)


@deprecated
def export_petri_as_string(petrinet, marking, final_marking=None, stochastic_map=None, export_prom5=False):
    """
    Parameters
    ----------
    petrinet: :class:`pm4py.entities.petri.petrinet.PetriNet`
        Petri net
    marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Marking
    final_marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Final marking (optional)
    stochastic_map
        (only for stochastics) map that associates to each transition a probability distribution
    export_prom5
        Enables exporting PNML files in a format that is ProM5-friendly

    Returns
    ----------
    string
        Petri net as string
    """
    return versions.pnml.export_petri_as_string(petrinet, marking, final_marking=final_marking,
                                                stochastic_map=stochastic_map, export_prom5=export_prom5)


@deprecated
def export_net(petrinet, marking, output_filename, final_marking=None, stochastic_map=None, export_prom5=False):
    """
    Export a Petrinet to a PNML file

    Parameters
    ----------
    petrinet: :class:`pm4py.entities.petri.petrinet.PetriNet`
        Petri net
    marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Marking
    final_marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Final marking (optional)
    output_filename:
        Absolute output file name for saving the pnml file
    stochastic_map
        (only for stochastics) map that associates to each transition a probability distribution
    export_prom5
        Enables exporting PNML files in a format that is ProM5-friendly
    """
    return versions.pnml.export_net(petrinet, marking, output_filename, final_marking=final_marking,
                                    stochastic_map=stochastic_map, export_prom5=export_prom5)

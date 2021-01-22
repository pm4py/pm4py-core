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
def convert_to_event_log(obj):
    """
    Converts a log object to an event log

    Parameters
    -------------
    obj
        Log object

    Returns
    -------------
    log
        Event log object
    """
    from pm4py.objects.conversion.log import converter
    log = converter.apply(obj, variant=converter.Variants.TO_EVENT_LOG)
    return log


def convert_to_event_stream(obj):
    """
    Converts a log object to an event stream

    Parameters
    --------------
    obj
        Log object

    Returns
    --------------
    stream
        Event stream object
    """
    from pm4py.objects.conversion.log import converter
    stream = converter.apply(obj, variant=converter.Variants.TO_EVENT_STREAM)
    return stream


def convert_to_dataframe(obj):
    """
    Converts a log object to a dataframe

    Parameters
    --------------
    obj
        Log object

    Returns
    --------------
    df
        Dataframe
    """
    from pm4py.objects.conversion.log import converter
    df = converter.apply(obj, variant=converter.Variants.TO_DATA_FRAME)
    return df


def convert_to_bpmn(*args):
    """
    Converts an object to a BPMN diagram

    Parameters
    --------------
    *args
        Object (process tree)

    Returns
    --------------
    bpmn_diagram
        BPMN diagram
    """
    from pm4py.objects.process_tree.process_tree import ProcessTree
    from pm4py.objects.bpmn.bpmn_graph import BPMN

    if isinstance(args[0], BPMN):
        # the object is already a BPMN
        return args[0]
    elif isinstance(args[0], ProcessTree):
        from pm4py.objects.conversion.process_tree.variants import to_bpmn
        return to_bpmn.apply(args[0])
    else:
        # try to convert the object to a Petri net. Then, use the PM4Py PN-to-BPMN converter
        # to get the BPMN object
        try:
            net, im, fm = convert_to_petri_net(*args)
            from pm4py.objects.conversion.wf_net.variants import to_bpmn
            return to_bpmn.apply(net, im, fm)
        except:
            # don't do nothing and throw the following exception
            pass
    # if no conversion is done, then the format of the arguments is unsupported
    raise Exception("unsupported conversion of the provided object to BPMN")


def convert_to_petri_net(*args):
    """
    Converts an object to an (accepting) Petri net

    Parameters
    --------------
    *args
        Object (process tree, BPMN)

    Returns
    --------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    from pm4py.objects.process_tree.process_tree import ProcessTree
    from pm4py.objects.bpmn.bpmn_graph import BPMN
    from pm4py.objects.heuristics_net.net import HeuristicsNet
    from pm4py.objects.petri.petrinet import PetriNet
    if isinstance(args[0], PetriNet):
        # the object is already a Petri net
        return args[0], args[1], args[2]
    elif isinstance(args[0], ProcessTree):
        from pm4py.objects.conversion.process_tree.variants import to_petri_net
        return to_petri_net.apply(args[0])
    elif isinstance(args[0], BPMN):
        from pm4py.objects.conversion.bpmn.variants import to_petri_net
        return to_petri_net.apply(args[0])
    elif isinstance(args[0], HeuristicsNet):
        from pm4py.objects.conversion.heuristics_net.variants import to_petri_net
        return to_petri_net.apply(args[0])
    elif isinstance(args[0], dict):
        # DFG
        from pm4py.objects.conversion.dfg.variants import to_petri_net_activity_defines_place
        return to_petri_net_activity_defines_place.apply(args[0], parameters={
            to_petri_net_activity_defines_place.Parameters.START_ACTIVITIES: args[1],
            to_petri_net_activity_defines_place.Parameters.END_ACTIVITIES: args[2]})
    # if no conversion is done, then the format of the arguments is unsupported
    raise Exception("unsupported conversion of the provided object to Petri net")


def convert_to_process_tree(*args):
    """
    Converts an object to a process tree

    Parameters
    --------------
    *args
        Object (Petri net, BPMN)

    Returns
    --------------
    tree
        Process tree (when the model is block-structured)
    """
    from pm4py.objects.process_tree.process_tree import ProcessTree
    from pm4py.objects.petri.petrinet import PetriNet
    if isinstance(args[0], ProcessTree):
        # the object is already a process tree
        return args[0]

    if isinstance(args[0], PetriNet):
        net, im, fm = args[0], args[1], args[2]
    else:
        net, im, fm = convert_to_petri_net(*args)

    from pm4py.objects.conversion.wf_net.variants import to_process_tree
    tree = to_process_tree.apply(net, im, fm)
    if tree is not None:
        return tree

    raise Exception("the object represents a model that cannot be represented as a process tree!")

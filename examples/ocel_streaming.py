import pm4py
import os
from pm4py.streaming.stream import live_event_stream
from pm4py.streaming.util import event_stream_printer
from pm4py.streaming.conversion import ocel_flatts_distributor
from pm4py.objects.ocel.util import ocel_iterator


def execute_script():
    ocel = pm4py.read_ocel(os.path.join("..", "tests", "input_data", "ocel", "example_log.jsonocel"))
    # we wants to use the traditional algorithms for streaming also on object-centric event logs.
    # for this purpose, first we create two different event streams, one for the "order" object type
    # and one for the "element" object type.
    order_stream = live_event_stream.LiveEventStream()
    element_stream = live_event_stream.LiveEventStream()
    # Then, we register an algorithm for every one of them, which is a simple printer of the received events.
    order_stream_printer = event_stream_printer.EventStreamPrinter()
    element_stream_printer = event_stream_printer.EventStreamPrinter()
    order_stream.register(order_stream_printer)
    element_stream.register(element_stream_printer)
    # Then, we create the distributor object.
    # This registers different event streams for different object types.
    flatts_distributor = ocel_flatts_distributor.OcelFlattsDistributor()
    flatts_distributor.register("order", order_stream)
    flatts_distributor.register("element", element_stream)
    order_stream.start()
    element_stream.start()
    # in this way, we iterate over the events of an OCEL
    for ev in ocel_iterator.apply(ocel):
        # ... and the OCEL event is sent to all the "flattened" event streams.
        flatts_distributor.append(ev)
        # since the "flattened" event streams register a printer each, what we get is a print
        # of all the events that reach these instances.
    order_stream.stop()
    element_stream.stop()


if __name__ == "__main__":
    execute_script()

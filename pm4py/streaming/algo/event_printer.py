from pm4py.streaming.algo import interface
from pm4py.objects.log.importer.xes import factory as xes_imp
import os
from pm4py.objects.conversion.log.versions import to_live_event_stream


class EventPrinter(interface.StreamingAlgorithm):

    def receive(self, event):
        print(event)


if __name__ == "__main__":
    log_path = os.path.join("..", "..", "..", "tests", "input_data", "roadtraffic50traces.xes")
    log = xes_imp.apply(log_path)
    stream = to_live_event_stream.apply(log)
    stream.register(EventPrinter())
    stream.start()

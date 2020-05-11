from pm4py.streaming.algo import interface
import os


class EventPrinter(interface.StreamingAlgorithm):

    def receive(self, event):
        print(event)


if __name__ == "__main__":
    from pm4py.objects.log.importer.xes import importer as xes_imp
    from pm4py.objects.conversion.log.variants import to_live_event_stream
    log_path = os.path.join("..", "..", "..", "tests", "input_data", "roadtraffic50traces.xes")
    log = xes_imp.apply(log_path)
    stream = to_live_event_stream.apply(log)
    stream.register(EventPrinter())
    stream.start()

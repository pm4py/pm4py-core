from pm4py.streaming.algo.interface import StreamingAlgorithm


class EventStreamPrinter(StreamingAlgorithm):
    def __init__(self):
        StreamingAlgorithm.__init__(self)

    def _process(self, event):
        print("event received:", event)

    def _current_result(self):
        pass

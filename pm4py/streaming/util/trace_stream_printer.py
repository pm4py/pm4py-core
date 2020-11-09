from pm4py.streaming.algo.interface import StreamingAlgorithm


class TraceStreamPrinter(StreamingAlgorithm):
    def __init__(self):
        StreamingAlgorithm.__init__(self)

    def _process(self, trace):
        print("trace received:", trace)

    def _current_result(self):
        pass

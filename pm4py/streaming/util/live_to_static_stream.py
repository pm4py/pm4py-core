from pm4py.streaming.algo.interface import StreamingAlgorithm
from pm4py.objects.log.obj import EventStream


class LiveToStaticStream(StreamingAlgorithm):
    static_stream = None

    def __init__(self):
        self.static_stream = EventStream()
        StreamingAlgorithm.__init__(self)

    def _process(self, event):
        self.static_stream.append(event)

    def _current_result(self):
        return self.static_stream

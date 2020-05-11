import os
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.serialization import factory as serialization_factory
from pm4py.objects.log.deserialization import factory as deserialization_factory
from pm4py.objects.conversion.log import factory as log_conf_factory


if __name__ == "__main__":
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    stream = log_conf_factory.apply(log, variant=log_conf_factory.TO_EVENT_STREAM)

    stream_bytes = serialization_factory.apply(stream)
    log_bytes = serialization_factory.apply(log)

    stream_rebuilt = deserialization_factory.apply(stream_bytes, variant=deserialization_factory.DEFAULT_EVENT_STREAM)
    log_rebuild = deserialization_factory.apply(log_bytes, variant=deserialization_factory.DEFAULT_EVENT_LOG)

    print(stream_rebuilt)
    print(log_rebuild)

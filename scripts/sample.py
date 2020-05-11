from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.importer.xes import importer as xes_importer

log = xes_importer.apply('../tests/input_data/running-example.xes')
print(log[0])
df = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)
print(df)


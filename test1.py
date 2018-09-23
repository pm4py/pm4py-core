from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.algo.filtering.tracelog.variants import variants_filter

log = xes_importer.import_log("tests\\inputData\\running-example.xes")
variants = variants_filter.get_variants(log)
print(variants)
log1 = variants_filter.apply(log, ["register request,examine casually,check ticket,decide,reinitiate request,examine thoroughly,check ticket,decide,pay compensation"], parameters={"positive":False})
print(len(log1))
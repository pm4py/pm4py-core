from pm4py.algo.discovery.dfg.variants import native, performance, freq_triples, case_attributes, clean
import importlib.util

if importlib.util.find_spec("polars"):
    from pm4py.algo.discovery.dfg.variants import clean_polars

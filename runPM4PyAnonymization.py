import pm4py
from pm4py.algo.anonymization.pripel import algorithm as pripel
from pm4py.algo.anonymization.trace_variant_query import algorithm as tvq_algorithm

log = pm4py.read_xes('SepsisCases-EventLog.xes')
epsilon = 0.1

tvqLaplace = tvq_algorithm.apply(log=log, variant=tvq_algorithm.Variants.LAPLACE,
                                 parameters={"epsilon": epsilon, "p": 1, "k": 4})
print(len(tvqLaplace))

#tvqSaCoFa = tvq_algorithm.apply(log=log, variant=tvq_algorithm.Variants.SACOFA,
#                                parameters={"epsilon": epsilon, "p": 1, "k": 2})
#anonymLogSaCoFa = pripel.apply(log=log, traceVariantQuery=tvqSaCoFa, parameters={"epsilon": epsilon})
anonymLogLaplace = pripel.apply(log=log, traceVariantQuery=tvqLaplace, parameters={"epsilon": epsilon})

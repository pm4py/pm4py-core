from typing import List, Tuple, Any, Counter

UnivariateCompressedTrace = List[Any]
MultivariateCompressedTrace = List[Tuple[Any]]
UCT = UnivariateCompressedTrace
MCT = MultivariateCompressedTrace

UnivariateCompressedLog = List[UCT]
MultivariateCompressedLog = List[MCT]
UCL = UnivariateCompressedLog
MCL = MultivariateCompressedLog

UnivariateLookupTable = List[Any]
ULT = UnivariateLookupTable
MultivariateLookupTable = List[List[Any]]
MLT = MultivariateLookupTable

UnivariateVariantCompressedLog = Counter[Tuple[Any]]
UVCL = UnivariateVariantCompressedLog

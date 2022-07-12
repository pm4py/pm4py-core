from typing import List, Tuple, Any

class UnivariateCompressedLog(List[List[int]]):
    pass

class MultivariateCompressedLog(List[List[Tuple[int]]]):
    pass

class UnivariateLookupTable(List[Any]):
    pass

class MultivariateLookupTable(List[List[Any]]):
    pass

UCL = UnivariateCompressedLog
MCL = MultivariateCompressedLog

ULT = UnivariateLookupTable
MLT = MultivariateLookupTable
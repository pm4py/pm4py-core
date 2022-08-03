from typing import List, Tuple, Any


class UnivariateCompressedTrace(List[Any]):
    pass


class MultivariateCompressedTrace(List[Tuple[Any]]):
    pass


class UnivariateCompressedLog(List[UnivariateCompressedTrace]):
    pass


class MultivariateCompressedLog(List[MultivariateCompressedTrace]):
    pass


class UnivariateLookupTable(List[Any]):
    pass


class MultivariateLookupTable(List[List[Any]]):
    pass


UCT = UnivariateCompressedTrace
MCT = MultivariateCompressedTrace

UCL = UnivariateCompressedLog
MCL = MultivariateCompressedLog

ULT = UnivariateLookupTable
MLT = MultivariateLookupTable

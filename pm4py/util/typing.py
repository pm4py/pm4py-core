from typing import Tuple, Dict, List, Any

TemporalProfile = Dict[Tuple[str, str], Tuple[float, float]]
TemporalProfileConformanceResults = List[List[Tuple[float, float, float, float]]]
TemporalProfileStreamingConfResults = Dict[str, List[Tuple[float, float, float, float]]]

AlignmentResult = Dict[str, Any]
ListAlignments = List[AlignmentResult]

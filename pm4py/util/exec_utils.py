from enum import Enum


def unroll(value):
    if isinstance(value, Enum):
        return value.value
    return value


# this function can be moved to a util when string values of the parameters are no longer supported. (or is no longer needed ;-))
def get_param_value(p, parameters, default):
    if parameters is None:
        return unroll(default)
    unrolled_parameters = {}
    for p0 in parameters:
        unrolled_parameters[unroll(p0)] = parameters[p0]
    if p in parameters:
        val = parameters[p]
        return unroll(val)
    up = unroll(p)
    if up in unrolled_parameters:
        val = unrolled_parameters[up]
        return unroll(val)
    return unroll(default)


def get_variant(variant):
    if isinstance(variant, Enum):
        return variant.value
    return variant

from pm4py.algo.sna.transformer.pandas.versions import basic, full

BASIC = "basic"
FULL = "full"

VERSIONS = {BASIC: basic.apply, FULL: full.apply}

def apply(df, parameters=None, variant=FULL):
    return VERSIONS[variant](df, parameters=parameters)

from pm4py.algo.enhancement.sna.transformer.pandas.versions import basic, full

BASIC = "basic"
FULL = "full"

VERSIONS = {BASIC: basic.apply, FULL: full.apply}

def apply(df, parameters=None, variant=FULL):
    """
    Create a matrix from the Pandas dataframe

    Parameters
    ------------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm:
            PARAMETER_CONSTANT_RESOURCE_KEY -> attribute key that contains the resource
            PARAMETER_CONSTANT_CASEID_KEY -> attribute key that contains the case ID
            PARAMETER_CONSTANT_TIMESTAMP_KEY -> attribute key that contains the timestamp
            sort_caseid_required -> Specify if a sort on the Case ID is required
            sort_timestamp_along_case_id -> Specifying if sorting by timestamp along the CaseID is required
    variant
        Possible variants of the algorithm, including: basic, full

    Returns
    ------------
    mco
        SNA Matrix container object
    """
    return VERSIONS[variant](df, parameters=parameters)

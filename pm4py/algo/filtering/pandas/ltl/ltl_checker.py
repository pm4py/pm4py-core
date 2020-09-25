from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util.xes_constants import DEFAULT_NAME_KEY, DEFAULT_RESOURCE_KEY, DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_CASEID_KEY, \
    PARAMETER_CONSTANT_RESOURCE_KEY, PARAMETER_CONSTANT_TIMESTAMP_KEY
from enum import Enum
from pm4py.util import exec_utils, pandas_utils, constants


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ATTRIBUTE_KEY = PARAMETER_CONSTANT_ATTRIBUTE_KEY
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    RESOURCE_KEY = PARAMETER_CONSTANT_RESOURCE_KEY
    POSITIVE = "positive"
    ENABLE_TIMESTAMP = "enable_timestamp"
    TIMESTAMP_DIFF_BOUNDARIES = "timestamp_diff_boundaries"


POSITIVE = Parameters.POSITIVE
ENABLE_TIMESTAMP = Parameters.ENABLE_TIMESTAMP
TIMESTAMP_DIFF_BOUNDARIES = Parameters.TIMESTAMP_DIFF_BOUNDARIES


def A_eventually_B(df0, A, B, parameters=None):
    """
    Applies the A eventually B rule

    Parameters
    ------------
    df0
        Dataframe
    A
        A Attribute value
    B
        B Attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A and B and in which A was eventually followed by B
        - If False, returns all the cases not containing A or B, or in which an instance of A was not eventually
        followed by an instance of B

    Returns
    ------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    enable_timestamp = exec_utils.get_param_value(Parameters.ENABLE_TIMESTAMP, parameters, False)
    timestamp_diff_boundaries = exec_utils.get_param_value(Parameters.TIMESTAMP_DIFF_BOUNDARIES, parameters, [])

    colset = [case_id_glue, attribute_key]
    if enable_timestamp:
        colset.append(timestamp_key)

    df = df0.copy()
    df = df[colset]
    df = pandas_utils.insert_index(df)
    df_A = df[df[attribute_key] == A].copy()
    df_B = df[df[attribute_key] == B].copy()
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna()
    df_join["@@diffindex"] = df_join[constants.DEFAULT_INDEX_KEY+"_2"] - df_join[constants.DEFAULT_INDEX_KEY]
    df_join = df_join[df_join["@@diffindex"] > 0]

    if enable_timestamp:
        df_join["@@difftimestamp"] = (df_join[timestamp_key + "_2"] - df_join[timestamp_key]).astype('timedelta64[s]')
        if timestamp_diff_boundaries:
            df_join = df_join[df_join["@@difftimestamp"] >= timestamp_diff_boundaries[0][0]]
            df_join = df_join[df_join["@@difftimestamp"] <= timestamp_diff_boundaries[0][1]]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join.set_index(case_id_glue).index

    if positive:
        return df0[i1.isin(i2)]
    else:
        return df0[~i1.isin(i2)]


def A_eventually_B_eventually_C(df0, A, B, C, parameters=None):
    """
    Applies the A eventually B eventually C rule

    Parameters
    ------------
    df0
        Dataframe
    A
        A Attribute value
    B
        B Attribute value
    C
        C Attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A, B and C and in which A was eventually followed by B and B was eventually followed by C
        - If False, returns all the cases not containing A or B or C, or in which an instance of A was not eventually
        followed by an instance of B or an instance of B was not eventually followed by C

    Returns
    ------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    enable_timestamp = exec_utils.get_param_value(Parameters.ENABLE_TIMESTAMP, parameters, False)
    timestamp_diff_boundaries = exec_utils.get_param_value(Parameters.TIMESTAMP_DIFF_BOUNDARIES, parameters, [])

    colset = [case_id_glue, attribute_key]
    if enable_timestamp:
        colset.append(timestamp_key)

    df = df0.copy()
    df = df[colset]
    df = pandas_utils.insert_index(df)
    df_A = df[df[attribute_key] == A].copy()
    df_B = df[df[attribute_key] == B].copy()
    df_C = df[df[attribute_key] == C].copy()
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")
    df_C["@@conceptname"] = df_C[case_id_glue]
    df_C = df_C.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna()
    df_join["@@diffindex"] = df_join[constants.DEFAULT_INDEX_KEY+"_2"] - df_join[constants.DEFAULT_INDEX_KEY]
    df_join = df_join[df_join["@@diffindex"] > 0]
    df_join = df_join.join(df_C, on=case_id_glue, rsuffix="_3").dropna()
    df_join["@@diffindex2"] = df_join[constants.DEFAULT_INDEX_KEY+"_3"] - df_join[constants.DEFAULT_INDEX_KEY+"_2"]
    df_join = df_join[df_join["@@diffindex2"] > 0]

    if enable_timestamp:
        df_join["@@difftimestamp"] = (df_join[timestamp_key + "_2"] - df_join[timestamp_key]).astype('timedelta64[s]')
        df_join["@@difftimestamp2"] = (df_join[timestamp_key + "_3"] - df_join[timestamp_key + "_2"]).astype(
            'timedelta64[s]')
        if timestamp_diff_boundaries:
            df_join = df_join[df_join["@@difftimestamp"] >= timestamp_diff_boundaries[0][0]]
            df_join = df_join[df_join["@@difftimestamp"] <= timestamp_diff_boundaries[0][1]]
            df_join = df_join[df_join["@@difftimestamp2"] >= timestamp_diff_boundaries[1][0]]
            df_join = df_join[df_join["@@difftimestamp2"] <= timestamp_diff_boundaries[1][1]]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join.set_index(case_id_glue).index

    if positive:
        return df0[i1.isin(i2)]
    else:
        return df0[~i1.isin(i2)]


def A_eventually_B_eventually_C_eventually_D(df0, A, B, C, D, parameters=None):
    """
    Applies the A eventually B eventually C rule

    Parameters
    ------------
    df0
        Dataframe
    A
        A Attribute value
    B
        B Attribute value
    C
        C Attribute value
    D
        D Attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A, B, C and D and in which A was eventually followed by B
            and B was eventually followed by C and C was eventually followed by D
        - If False, returns all the cases not containing A or B or C or D, or in which an instance of A was not eventually
            followed by an instance of B or an instance of B was not eventually followed by C or an instance of C was
            not eventually followed by D

    Returns
    ------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    enable_timestamp = exec_utils.get_param_value(Parameters.ENABLE_TIMESTAMP, parameters, False)
    timestamp_diff_boundaries = exec_utils.get_param_value(Parameters.TIMESTAMP_DIFF_BOUNDARIES, parameters, [])

    colset = [case_id_glue, attribute_key]
    if enable_timestamp:
        colset.append(timestamp_key)

    df = df0.copy()
    df = df[colset]
    df = pandas_utils.insert_index(df)
    df_A = df[df[attribute_key] == A].copy()
    df_B = df[df[attribute_key] == B].copy()
    df_C = df[df[attribute_key] == C].copy()
    df_D = df[df[attribute_key] == D].copy()

    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")
    df_C["@@conceptname"] = df_C[case_id_glue]
    df_C = df_C.groupby(case_id_glue).last().set_index("@@conceptname")
    df_D["@@conceptname"] = df_D[case_id_glue]
    df_D = df_D.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna()
    df_join["@@diffindex"] = df_join[constants.DEFAULT_INDEX_KEY+"_2"] - df_join[constants.DEFAULT_INDEX_KEY]
    df_join = df_join[df_join["@@diffindex"] > 0]
    df_join = df_join.join(df_C, on=case_id_glue, rsuffix="_3").dropna()
    df_join["@@diffindex2"] = df_join[constants.DEFAULT_INDEX_KEY+"_3"] - df_join[constants.DEFAULT_INDEX_KEY+"_2"]
    df_join = df_join[df_join["@@diffindex2"] > 0]
    df_join = df_join.join(df_D, on=case_id_glue, rsuffix="_4").dropna()
    df_join["@@diffindex3"] = df_join[constants.DEFAULT_INDEX_KEY+"_4"] - df_join[constants.DEFAULT_INDEX_KEY+"_3"]
    df_join = df_join[df_join["@@diffindex3"] > 0]

    if enable_timestamp:
        df_join["@@difftimestamp"] = (df_join[timestamp_key + "_2"] - df_join[timestamp_key]).astype('timedelta64[s]')
        df_join["@@difftimestamp2"] = (df_join[timestamp_key + "_3"] - df_join[timestamp_key + "_2"]).astype(
            'timedelta64[s]')
        df_join["@@difftimestamp3"] = (df_join[timestamp_key + "_4"] - df_join[timestamp_key + "_3"]).astype(
            'timedelta64[s]')

        if timestamp_diff_boundaries:
            df_join = df_join[df_join["@@difftimestamp"] >= timestamp_diff_boundaries[0][0]]
            df_join = df_join[df_join["@@difftimestamp"] <= timestamp_diff_boundaries[0][1]]
            df_join = df_join[df_join["@@difftimestamp2"] >= timestamp_diff_boundaries[1][0]]
            df_join = df_join[df_join["@@difftimestamp2"] <= timestamp_diff_boundaries[1][1]]
            df_join = df_join[df_join["@@difftimestamp3"] >= timestamp_diff_boundaries[2][0]]
            df_join = df_join[df_join["@@difftimestamp3"] <= timestamp_diff_boundaries[2][1]]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join.set_index(case_id_glue).index

    if positive:
        return df0[i1.isin(i2)]
    else:
        return df0[~i1.isin(i2)]


def A_next_B_next_C(df0, A, B, C, parameters=None):
    """
    Applies the A net B next C rule

    Parameters
    ------------
    df0
        Dataframe
    A
        A Attribute value
    B
        B Attribute value
    C
        C Attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A, B and C and in which A was directly followed by B and B was directly followed by C
        - If False, returns all the cases not containing A or B or C, or in which none instance of A was directly
        followed by an instance of B and B was directly followed by C

    Returns
    ------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    df = df0.copy()
    df = df[[case_id_glue, attribute_key]]
    df = pandas_utils.insert_index(df)
    df_A = df[df[attribute_key] == A].copy()
    df_B = df[df[attribute_key] == B].copy()
    df_C = df[df[attribute_key] == C].copy()
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")
    df_C["@@conceptname"] = df_C[case_id_glue]
    df_C = df_C.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna().join(df_C, on=case_id_glue, rsuffix="_3").dropna()
    df_join["@@diffindex"] = df_join[constants.DEFAULT_INDEX_KEY+"_2"] - df_join[constants.DEFAULT_INDEX_KEY]
    df_join["@@diffindex2"] = df_join[constants.DEFAULT_INDEX_KEY+"_3"] - df_join[constants.DEFAULT_INDEX_KEY+"_2"]
    df_join = df_join[df_join["@@diffindex"] == 1]
    df_join = df_join[df_join["@@diffindex2"] == 1]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join.set_index(case_id_glue).index

    if positive:
        return df0[i1.isin(i2)]
    else:
        return df0[~i1.isin(i2)]


def four_eyes_principle(df0, A, B, parameters=None):
    """
    Verifies the Four Eyes Principle given A and B

    Parameters
    -------------
    df0
        Dataframe
    A
        A attribute value
    B
        B attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - if True, then filters all the cases containing A and B which have empty intersection between the set
          of resources doing A and B
        - if False, then filters all the cases containing A and B which have no empty intersection between the set
          of resources doing A and B

    Returns
    --------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, DEFAULT_RESOURCE_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    df = df0.copy()
    df = df[[case_id_glue, attribute_key, resource_key]]

    df_A = df[df[attribute_key] == A].copy()
    df_B = df[df[attribute_key] == B].copy()
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna()
    df_join_pos = df_join[df_join[resource_key] == df_join[resource_key + "_2"]]
    df_join_neg = df_join[df_join[resource_key] != df_join[resource_key + "_2"]]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join_pos.set_index(case_id_glue).index
    i3 = df_join_neg.set_index(case_id_glue).index

    if positive:
        return df0[i1.isin(i3) & ~i1.isin(i2)]
    else:
        return df0[i1.isin(i2)]


def attr_value_different_persons(df0, A, parameters=None):
    """
    Checks whether an attribute value is assumed on events done by different resources

    Parameters
    ------------
    df0
        Dataframe
    A
        A attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
            - if True, then filters all the cases containing occurrences of A done by different resources
            - if False, then filters all the cases not containing occurrences of A done by different resources

    Returns
    -------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, DEFAULT_RESOURCE_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    df = df0.copy()
    df = df[[case_id_glue, attribute_key, resource_key]]

    df_A = df[df[attribute_key] == A].copy()
    df_B = df[df[attribute_key] == A].copy()
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna()
    df_join_neg = df_join[df_join[resource_key] != df_join[resource_key + "_2"]]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join_neg.set_index(case_id_glue).index

    if positive:
        return df0[i1.isin(i2)]
    else:
        return df0[~i1.isin(i2)]

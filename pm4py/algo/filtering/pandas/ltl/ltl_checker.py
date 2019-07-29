from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY, DEFAULT_RESOURCE_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_CASEID_KEY, \
    PARAMETER_CONSTANT_RESOURCE_KEY

POSITIVE = "positive"


def A_eventually_B(df, A, B, parameters=None):
    """
    Applies the A eventually B rule

    Parameters
    ------------
    df
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

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    df = df[[case_id_glue, attribute_key]]
    df["@@index"] = df.index
    df_A = df[df[attribute_key] == A]
    df_B = df[df[attribute_key] == B]
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna()
    df_join["@@diffindex"] = df_join["@@index_2"] - df_join["@@index"]
    df_join = df_join[df_join["@@diffindex"] > 0]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join.set_index(case_id_glue).index

    if positive:
        return df[i1.isin(i2)]
    else:
        return df[~i1.isin(i2)]


def A_eventually_B_eventually_C(df, A, B, C, parameters=None):
    """
    Applies the A eventually B eventually C rule

    Parameters
    ------------
    df
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

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    df = df[[case_id_glue, attribute_key]]
    df["@@index"] = df.index
    df_A = df[df[attribute_key] == A]
    df_B = df[df[attribute_key] == B]
    df_C = df[df[attribute_key] == C]
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")
    df_C["@@conceptname"] = df_C[case_id_glue]
    df_C = df_C.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna().join(df_C, on=case_id_glue, rsuffix="_3").dropna()
    df_join["@@diffindex"] = df_join["@@index_2"] - df_join["@@index"]
    df_join["@@diffindex2"] = df_join["@@index_3"] - df_join["@@index_2"]
    df_join = df_join[df_join["@@diffindex"] > 0]
    df_join = df_join[df_join["@@diffindex2"] > 0]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join.set_index(case_id_glue).index

    if positive:
        return df[i1.isin(i2)]
    else:
        return df[~i1.isin(i2)]


def A_next_B_next_C(df, A, B, C, parameters=None):
    """
    Applies the A net B next C rule

    Parameters
    ------------
    df
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

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    df = df[[case_id_glue, attribute_key]]
    df["@@index"] = df.index
    df_A = df[df[attribute_key] == A]
    df_B = df[df[attribute_key] == B]
    df_C = df[df[attribute_key] == C]
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")
    df_C["@@conceptname"] = df_C[case_id_glue]
    df_C = df_C.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna().join(df_C, on=case_id_glue, rsuffix="_3").dropna()
    df_join["@@diffindex"] = df_join["@@index_2"] - df_join["@@index"]
    df_join["@@diffindex2"] = df_join["@@index_3"] - df_join["@@index_2"]
    df_join = df_join[df_join["@@diffindex"] == 1]
    df_join = df_join[df_join["@@diffindex2"] == 1]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join.set_index(case_id_glue).index

    if positive:
        return df[i1.isin(i2)]
    else:
        return df[~i1.isin(i2)]


def four_eyes_principle(df, A, B, parameters=None):
    """
    Verifies the Four Eyes Principle given A and B

    Parameters
    -------------
    df
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

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    resource_key = parameters[
        PARAMETER_CONSTANT_RESOURCE_KEY] if PARAMETER_CONSTANT_RESOURCE_KEY in parameters else DEFAULT_RESOURCE_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    df = df[[case_id_glue, attribute_key, resource_key]]

    df_A = df[df[attribute_key] == A]
    df_B = df[df[attribute_key] == B]
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna()
    df_join_pos = df_join[df_join[resource_key] == df_join[resource_key + "_2"]]
    df_join_neg = df_join[df_join[resource_key] != df_join[resource_key + "_2"]]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join_pos.set_index(case_id_glue).index
    i3 = df_join_neg.set_index(case_id_glue).index

    if positive:
        return df[i1.isin(i3) & ~i1.isin(i2)]
    else:
        return df[i1.isin(i2)]


def attr_value_different_persons(df, A, parameters=None):
    """
    Checks whether an attribute value is assumed on events done by different resources

    Parameters
    ------------
    df
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

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    resource_key = parameters[
        PARAMETER_CONSTANT_RESOURCE_KEY] if PARAMETER_CONSTANT_RESOURCE_KEY in parameters else DEFAULT_RESOURCE_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    df = df[[case_id_glue, attribute_key, resource_key]]

    df_A = df[df[attribute_key] == A]
    df_B = df[df[attribute_key] == A]
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna()
    df_join_neg = df_join[df_join[resource_key] != df_join[resource_key + "_2"]]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join_neg.set_index(case_id_glue).index

    if positive:
        return df[i1.isin(i2)]
    else:
        return df[~i1.isin(i2)]

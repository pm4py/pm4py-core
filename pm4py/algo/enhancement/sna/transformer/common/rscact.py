import numpy as np


def get_empty_rscact_matrix(mco):
    """
    Make an empty numpy matrix with the rows that are resources, and the columns that are activities

    Returns
    ------------
    rscact
        (empty) Resource-Activity matrix
    """
    if len(mco.activities_list) == 0:
        raise Exception("must provide full MCO dataframe")
    rscact = np.zeros([len(mco.resources_list), len(mco.activities_list)])  # +1 is just for considering <None>
    return rscact

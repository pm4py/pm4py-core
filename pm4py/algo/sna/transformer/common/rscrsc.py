import numpy as np


def get_empty_rscrsc_matrix(mco):
    """
    Make an empty numpy matrix with the rows and columns which are resource list

    Returns
    ------------
    rscrsc
        (empty) Resource-Resource matrix
    """
    rscrsc = np.zeros([len(mco.resources_list), len(mco.resources_list)])  # +1 is just for considering <None>
    return rscrsc

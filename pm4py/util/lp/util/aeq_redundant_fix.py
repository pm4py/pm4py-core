import numpy as np


def remove_redundant_rows(Aeq, beq):
    """
    Remove redundant rows from the equality matrixes

    Parameters
    -------------
    Aeq
        A equality matrix for the problem
    beq
        b equality matrix for the problem

    Returns
    -------------
    Aeq
        A equality matrix for the problem
    beq
        b equality matrix for the problem
    """
    if Aeq is not None and beq is not None:
        # remove rendundant rows
        i = 1
        while i <= Aeq.shape[0]:
            partial_rank = np.linalg.matrix_rank(Aeq[0:i, ])
            if i > partial_rank:
                Aeq = np.delete(Aeq, i - 1, 0)
                beq = np.delete(beq, i - 1, 0)
                continue
            i = i + 1

    return Aeq, beq

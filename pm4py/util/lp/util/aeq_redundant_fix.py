'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
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

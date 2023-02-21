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
import sys

import numpy as np

GS_SCORE = 1  # score has sensitivity of 1


def score(output_universes):
    return [x for x in np.flip(output_universes)]


def exp_mech(output_universes, epsilon):
    scores = score(output_universes)
    raw_prob = [np.exp((epsilon * x) / (2 * GS_SCORE)) for x in scores]
    i = 0
    for prob in raw_prob:
        if prob == float('inf'):
            raw_prob[i] = sys.float_info.max
        i += 1
    prob = np.exp(raw_prob - np.max(raw_prob))
    prob = prob / prob.sum()
    return np.random.choice(output_universes, p=prob)

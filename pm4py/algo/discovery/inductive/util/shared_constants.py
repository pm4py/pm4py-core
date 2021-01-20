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
"""
Shared constants useful for Inductive Miner application
"""


# LOOP_CONST_1: degree constant that the activity with the most higher degree shall have
# in order to be taken in consideration for the DO part
LOOP_CONST_1 = 0.2
# LOOP_CONST_2: degree constant that entering activities to the activity with the most higher degree
# shall have in order to be included in the LOOP part
LOOP_CONST_2 = 0.02
# LOOP_CONST_3: for activities not yet included in set1 or set2, if their degree is below this constant
# then they are included automatically in the LOOP/EXIT part
LOOP_CONST_3 = -0.2
# LOOP_CONST_4: constant that determine the automatic inclusion of an activity in the loop part
LOOP_CONST_4 = -0.7

# SEQ_SET1_CONST: constant on the degree of the activities that make them belonging to set1 in the
# sequential cut detection, if there is freedom about the placement
SEQ_SET1_CONST = 0.28
# SEQ_SET2_CONST: constant on the degree of the activities that make them belonging to set2 in the
# sequential cut detection, if there is freedom about the placement
SEQ_SET2_CONST = -0.28

# parallel cut constant (must be 0 to adhere to original implementation)
PAR_CUT_CONSTANT = 0

# default noise threshold
NOISE_THRESHOLD_IMD = 0.0
NOISE_THRESHOLD_IMF = 0.2

# recursion limit for IMDF
REC_LIMIT = 100000
# maximum threads execution time for reduction
RED_MAX_THR_EX_TIME = 10
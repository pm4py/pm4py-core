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
import logging

def empty_log(log):
    '''Returns bool if log is empty'''
    if len(log) == 0:
        logging.debug("empty_log")
        return True
    else:
        return False


def single_activity(log, activity_key):
    '''Returns bool if log consists of single activity only'''
    if log:
        if len(log[0]) >= 1:
            first_activity = log[0][0][activity_key]
            for i in range(0, len(log)):
                if len(log[i]) != 1 or log[i][0][activity_key] != first_activity:
                    return False                # if there is a trace that has a length not equal to 1, we return false

            # check if all traces consist of the same activity, therefore create dfg from log and get activities of that dfg
            logging_output = "single_activity: " + str(first_activity)
            logging.debug(logging_output)
            return True
        else:
            return False
    else:
        return False

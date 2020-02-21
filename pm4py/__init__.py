import time

time.clock = time.process_time

try:
    import pm4pycvxopt
except:
    pass

from pm4py import algo, evaluation, objects, util, visualization, statistics, streaming

__version__ = '1.2.11'
__doc__ = "Process Mining for Python"
__author__ = 'Fraunhofer Institute for Applied Technology'
__author_email__ = 'pm4py@fit.fraunhofer.de'
__maintainer__ = 'Fraunhofer Institute for Applied Technology'
__maintainer_email__ = "pm4py@fit.fraunhofer.de"

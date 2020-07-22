import logging
import pkgutil
import time

time.clock = time.process_time

try:
    import pm4pycvxopt
except:
    pass

from pm4py import util, objects, statistics, algo, visualization, evaluation, streaming, simulation

if pkgutil.find_loader("scipy"):
    pass
else:
    logging.error("scipy is not available. This can lead some features of PM4Py to not work correctly!")

if pkgutil.find_loader("sklearn"):
    pass
else:
    logging.error("scikit-learn is not available. This can lead some features of PM4Py to not work correctly!")

if pkgutil.find_loader("networkx"):
    pass
else:
    logging.error("networkx is not available. This can lead some features of PM4Py to not work correctly!")

__version__ = '1.3.5.1'
__doc__ = "Process Mining for Python (PM4Py)"
__author__ = 'Fraunhofer Institute for Applied Technology'
__author_email__ = 'pm4py@fit.fraunhofer.de'
__maintainer__ = 'Fraunhofer Institute for Applied Technology'
__maintainer_email__ = "pm4py@fit.fraunhofer.de"

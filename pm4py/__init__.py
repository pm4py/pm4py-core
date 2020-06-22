import time, pkgutil, logging

time.clock = time.process_time

from pm4py import util, objects, statistics, algo, visualization, evaluation, streaming, simulation

if pkgutil.find_loader("scipy"):
    import scipy
else:
    logging.error("scipy is not available. This can lead some features of PM4Py to not work correctly!")

if pkgutil.find_loader("sklearn"):
    import sklearn
else:
    logging.error("scikit-learn is not available. This can lead some features of PM4Py to not work correctly!")

if pkgutil.find_loader("networkx"):
    import networkx
else:
    logging.error("networkx is not available. This can lead some features of PM4Py to not work correctly!")

__version__ = '1.3.3'
__doc__ = "Process Mining for Python"
__author__ = 'Fraunhofer Institute for Applied Technology'
__author_email__ = 'pm4py@fit.fraunhofer.de'
__maintainer__ = 'Fraunhofer Institute for Applied Technology'
__maintainer_email__ = "pm4py@fit.fraunhofer.de"

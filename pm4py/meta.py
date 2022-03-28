__name__ = 'pm4py'
VERSION = '2.2.19.3'
__version__ = VERSION
__author__ = 'Fraunhofer Institute for Applied Technology'
__author_email__ = 'pm4py@fit.fraunhofer.de'
__maintainer__ = 'Fraunhofer Institute for Applied Technology'
__maintainer_email__ = "pm4py@fit.fraunhofer.de"

__doc__ = """
Process Mining for Python (``pm4py``)

The ``pm4py`` library is the most extensive open-source process mining library for ``python``.
In this API reference, all relevant functions of the library are listed.


* Importing / Exporting Log Files
    With PM4Py, the possibility to import/export event logs using the XES format is provided.
    Moreover, support for process mining computations on top of Pandas dataframes is provided, along
    with the possibility to convert between XES and Pandas dataframes.
    Also, support for object-centric event log (OCEL) is provided.
    
    * `Importing Log Files`_
    * `Exporting Log Files`_
    * `Conversions`_
* `Process Discovery`_
    Process Discovery algorithms want to find a suitable process model that describes the order of events/activities that are executed during a process execution.
* `Visualization`_
    We offer a set of visualizations for process models and statistics.
* `Conformance Checking`_
    Conformance checking is a techniques to compare a process model with an event log of the same process. The goal is to check if the event log conforms to the model, and, vice versa.
* `Statistics`_
    In this section, different statistics that could be computed on top of event logs are explained.
* `Filtering`_
    Filtering is the restriction of the event log to a subset of the behavior.
* `Machine Learning`_
    Possibility to transform an event log to a matrix of features in order to apply mainstream machine learning methods/libraries.
* `Simulation`_
    We offer different simulation algorithms, that starting from a model, are able to produce an output that follows the model and the different rules that have been provided by the user.
* `Object-Centric Process Mining`_
    Object-centric process mining is a novel branch which drops the assumption that an event is associated to a single case. In this way, an event can be related to different objects of different object types.

.. _Importing Log Files: pm4py.html#module-pm4py.read
.. _Exporting Log Files: pm4py.html#module-pm4py.write
.. _Conversions: pm4py.html#module-pm4py.convert
.. _Process Discovery: pm4py.html#module-pm4py.discovery
.. _Visualization: pm4py.html#module-pm4py.vis
.. _Conformance Checking: pm4py.html#module-pm4py.conformance
.. _Statistics: pm4py.html#module-pm4py.stats
.. _Filtering: pm4py.html#module-pm4py.filtering
.. _Machine Learning: pm4py.html#module-pm4py.ml
.. _Simulation: pm4py.html#module-pm4py.sim
.. _Object-Centric Process Mining: pm4py.html#module-pm4py.ocel

"""

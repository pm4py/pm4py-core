API Reference
=============
This page gives an overview of all public ``pm4py`` objects, functions and methods. 

Input (:mod:`pm4py.read`)
---------------------------------
``pm4py`` supports importing two different *event data* formats:

* ``.xes`` files; General interchange format for event data.
* ``.ocel`` files; Novel data format (under development) for multi-dimensional event data.

In case an event log is stored as a ``.csv`` file, ``pandas`` can be used to directly import the event log as a ``data frame`` (`docs <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html>`_).
Both file formats are internally converted to ``pandas dataframes``, which are the default data structure used by all algorithms implemented in ``pm4py``.

Additional file formats that are supported are:

* ``.bpmn`` files; File format specifying process models in the *BPMN* process modeling formalism
* ``.dfg`` files; File format specifying *directly follows graphs* (also referred to as *process maps*)
* ``.pnml`` files; File format specifying *Petri net* models
* ``.ptml`` files; File format specifying *Process Tree* models


Output (:mod:`pm4py.write`)
-------------------------------------
Similarly to event data importing, ``pm4py`` supports export functionalities to:

* ``.bpmn`` files,
* ``.dfg`` files,
* ``.ocel`` files,
* ``.pnml`` files,
* ``.ptml`` files,
* ``.xes`` files.

Process Discovery (:mod:`pm4py.discovery`)
------------------------------------------
    Process Discovery algorithms discover a process model that describes the process execution, as stored in the event log.
* Visualization (:mod:`pm4py.vis`)
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




.. autosummary::
   :toctree: generated

   pm4py.discovery
   pm4py.read
   pm4py.read.read_bpmn
   pm4py.read.read_dfg
   pm4py.write
   
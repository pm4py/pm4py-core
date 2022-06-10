Welcome to pmp4y's Documentation!
===================================

``pm4py`` is a Python library implementing a variety of `process mining <https://en.wikipedia.org/wiki/Process_mining>`_ algorithms.

A simple example of pm4py in action:

.. code-block:: python

   import pm4py
   log = pm4py.read_xes('<path-to-xes-log-file.xes>')
   process_model = pm4py.discover_bpmn_inductive(log)
   pm4py.view_bpmn(process_model)
					

Contents
--------

.. toctree::
   :maxdepth: 2

   install
   getting_started
   api
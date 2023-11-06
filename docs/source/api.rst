API Reference
=============
This page provide the overview of the implementation that we have been working on:

Input (:mod:`pm4py.read`)
---------------------------------
Importing DCR Graphs is possible with the following formats:
  * ``.xml`` specificantion :meth:`pm4py.read.read_dcr_xml`: Imports a *DCR Graph* from a ``.xml`` file


Output (:mod:`pm4py.write`)
-------------------------------------
Exporting of DCR Graphs possible with the following format:
  * ``.xml`` specification :meth:`pm4py.write.write_dcr_xml`: Exports a *DCR Graph* to a ``.xml`` file



Process Discovery (:mod:`pm4py.discovery`)
------------------------------------------

Process mining of DCR Graphs, for determining a the control-flow of a the event log and map it to a graph:

  * :meth:`pm4py.discovery.discover_dcr`; discovers a *DCR Graph*.


Conformance Checking (:mod:`pm4py.conformance`)
-----------------------------------------------
Conformance checking techniques compare a process model with an event log of the same process. The goal is to check if the event log conforms to the model, and, vice versa.
DCR Graphs:

  * :meth:`pm4py.conformance.conformance_dcr`; conformance checking using the *DCR Graph*
  * :meth:`pm4py.conformance.optimal_alignment_dcr`; conformance checking using the *DCR Graph*



Overall List of Methods
------------------------------------------

.. autosummary::
   :toctree: generated

   pm4py.read
   pm4py.read.read_dcr_xml
   pm4py.write
   pm4py.write.write_dcr_xml
   pm4py.discovery
   pm4py.discovery.discover_dcr
   pm4py.conformance
   pm4py.conformance.conformance_dcr
   pm4py.conformance.optimal_alignment_dcr
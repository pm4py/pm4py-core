Getting Started/Examples
===============

Obtaining a Process Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For discovering a DCR Graphs process model, one can use the simplified interface created in order to perform underlying algorithm:rx.ist.psu.edu/viewdoc/download?doi=10.1.1.396.197&rep=rep1&type=pdf>`_. Consider the following code snippet. We discover a BPMN model (using a conversion from process tree to BPMN) using the inductive miner, based on the running example event data set.

.. code-block:: python3

    import pm4py

    if __name__ == "__main__":
        log = pm4py.read_xes('C:/Users/demo/Downloads/running-example.xes')
        graph,_ = pm4py.discover_dcr(log)

Note that we have yet to implement a visualization tool, however we have been working on as an extension to allow an overview, luckily our supervisor provided us a link to `DCR-js <https://github.com/hugoalopez-dtu/dcr-js>`_.
While it does give visualisation there is a need for creating optimal way points however we did not have time to figure that out sadly.

.. code-block:: python3

    import pm4py
    from pm4py.objects.dcr.export.exporter import Variants

    if __name__ == "__main__":
        log = pm4py.read_xes('C:/Users/demo/Downloads/running-example.xes')
        graph,_ = pm4py.discover_dcr(log)
        pm4py.write_dcr_xml(graph, "path/to/store/filename", variant=Variants.DCR_JS_PORTAL.value,"name of dcr graph")

It is also possible to retrieve the exported dcr.xml file py calling the importer, that will run through the xml,check for the different relations and assignments specified by the xml tags

.. code-block:: python3

    import pm4py
    from pm4py.objects.dcr.import.importer import Variants

    if __name__ == "__main__":
        log = pm4py.read_xes('C:/Users/demo/Downloads/running-example.xes')
        graph,_ = pm4py.discover_dcr(log)
        pm4py.read_dcr_xml(graph, "path/to/get/filename", variant=Variants.DCR_JS_PORTAL,"name of dcr graph")


This process will import a DCR Graph, for which it will instantiate a DCR_graph object

Conformance of DCR Graph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Conformance checking of DCR graph, we choose two different approaches, the rule based conformance check, that will replay a log and return a list of deviation and the fitness provided by that.

.. code-block:: python3

    import pm4py

    if __name__ == "__main__":
        log = pm4py.read_xes('C:/Users/demo/Downloads/running-example.xes')
        graph,_ = pm4py.discover_dcr(log)
        conf_res = pm4py.conformance(log, graph)

This will return a list of all the conformance results, if one wishes to compute the fitness of the model itself, one can perform the following:

.. code-block:: python3

    import pm4py

    if __name__ == "__main__":
        log = pm4py.read_xes('C:/Users/demo/Downloads/running-example.xes')
        graph,_ = pm4py.discover_dcr(log)
        conf_res = pm4py.conformance(log, graph)
        for j in conf_res:
            if j['deviations'] != []:
                collect = collect.union({tuple(x) for x in j['deviations']})

this will then determine the specific number of deviations type that happened during the run of an entire log. important to note that in this example, the same log for discovery is provided for conformance, which then will lead to a conf res with perfect fitness, as DCR discover perfectly fitting graphs.

For the alignment approach, we implemented a optimal alignment algorithm, that would compute and determine the optimal trace, together with the cost of alignment. The conformance results will return a list of alignment, cost, visited states and closed states, additionally, it will compute and return the move fitness of log moves and model moves.
the conformance.

.. code-block:: python3

    import pm4py

    if __name__ == "__main__":
        log = pm4py.read_xes('C:/Users/demo/Downloads/running-example.xes')
        graph,_ = pm4py.discover_dcr(log)
        conf_res = pm4py.optimal_alignment_dcr(log, graph)

Similarly to the the previous example, the fitness will be perfect, due to the property of the DisCoveR algorithm. This trace, will run through all iteration, and will return immediately when an optimal alignment has been found.

These functions that has been provided here are all a facade for the algortihm we have been working with and developed, and the implementation and documentation of them can be found with the modules.
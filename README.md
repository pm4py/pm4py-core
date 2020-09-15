# 👷 PM4Py
Process Mining for Python

Designed to be used in both academia and industry, PM4Py is the leading open source process mining platform written in Python, implementing _Petri nets_, _Open XES Importing/Exporting_, _CSV Importing/Exporting_, _Process Discovery_, _Conformance Checking_, and _BPMN Support_.

* **Documentation:** https://pm4py.fit.fraunhofer.de/
* **Source Code:** https://github.com/pm4py/pm4py-core
* **Bug reports:** https://github.com/pm4py/pm4py-core/issues

## Installing PM4Py

PM4Py is available on [PyPI](https://pypi.org/project/pm4py/):

`python -m pip install pm4py`

For more detailed instructions, see the [installation documentation](https://pm4py.fit.fraunhofer.de/install).

## Quickstart Guide
A very simple example, to whet your appetite:

```python
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.visualization.petrinet import visualizer as petri_visualizer

log = xes_importer.apply('<path-to-xes-log-file>')
net, initial_marking, final_marking = alpha_miner.apply(log)
gviz = petri_visualizer.apply(net, initial_marking, final_marking)
petri_visualizer.view(gviz)
```

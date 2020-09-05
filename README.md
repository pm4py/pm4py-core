# Welcome to Process Mining for Python!

PM4Py is a Python library that supports (state-of-the-art) process mining algorithms. 

It is completely open-source and intended to be used in both academia and industry projects.

The official website of the library is [http://pm4py.org/](http://pm4py.org/).

You can always check out (changes to) the source code at the GitHub repository.

# Examples
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

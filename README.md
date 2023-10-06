# pm4py
pm4py is a python library that supports (state-of-the-art) process mining algorithms in python. 
It is open source (licensed under GPL) and intended to be used in both academia and industry projects.
pm4py is a product of the Fraunhofer Institute for Applied Information Technology.

## Documentation / API
The full documentation of pm4py can be found at https://pm4py.fit.fraunhofer.de

## First Example
A very simple example, to whet your appetite:

```python
import pm4py

if __name__ == "__main__":
    log = pm4py.read_xes('<path-to-xes-log-file.xes>')
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log)
    pm4py.view_petri_net(net, initial_marking, final_marking, format="svg")
```

## Installation
pm4py can be installed on Python 3.9.x / 3.10.x / 3.11.x / 3.12.x by invoking:
*pip install -U pm4py*

pm4py is also running on older Python environments with different requirements sets, including:
- Python 3.8 (3.8.10): third_party/old_python_deps/requirements_py38.txt

## Requirements
pm4py depends on some other Python packages, with different levels of importance:
* *Essential requirements*: numpy, pandas, deprecation, networkx
* *Normal requirements* (installed by default with the pm4py package, important for mainstream usage): graphviz, intervaltree, lxml, matplotlib, pydotplus, pytz, scipy, stringdist, tqdm
* *Optional requirements* (not installed by default): scikit-learn, pyemd, pyvis, jsonschema, polars, openai, pywin32, python-dateutil, requests, workalendar

## Release Notes
To track the incremental updates, please refer to the *CHANGELOG* file.

## Third Party Dependencies
As scientific library in the Python ecosystem, we rely on external libraries to offer our features.
In the */third_party* folder, we list all the licenses of our direct dependencies.
Please check the */third_party/LICENSES_TRANSITIVE* file to get a full list of all transitive dependencies and the corresponding license.

## Citing pm4py
If you are using pm4py in your scientific work, please cite pm4py as follows:

**Alessandro Berti, Sebastiaan van Zelst, Daniel Schuster**. (2023). *PM4Py: A process mining library for Python*. Software Impacts, 17, 100556. [DOI](https://doi.org/10.1016/j.simpa.2023.100556) | [Article Link](https://www.sciencedirect.com/science/article/pii/S2665963823000933)

BiBTeX:

```bibtex
@article{pm4py,  
title = {PM4Py: A process mining library for Python},  
journal = {Software Impacts},  
volume = {17},  
pages = {100556},  
year = {2023},  
issn = {2665-9638},  
doi = {https://doi.org/10.1016/j.simpa.2023.100556},  
url = {https://www.sciencedirect.com/science/article/pii/S2665963823000933},  
author = {Alessandro Berti and Sebastiaan van Zelst and Daniel Schuster},  
}
```


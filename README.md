# PM4Py
PM4Py is a python library that supports (state-of-the-art) process mining algorithms in python. 
It is completely open source and intended to be used in both academia and industry projects.
PM4Py is a product of the Fraunhofer Institute for Applied Information Technology.

## Documentation / API
Full documentation of PM4Py is available at http://pm4py.org/

## First Example
A very simple example, to whet your appetite:

```python
import pm4py

log = pm4py.read_xes('<path_to_xes_file>')
process_model = pm4py.discover_bpmn_inductive(log)
pm4py.view_bpmn(process_model)
```

## Installation
PM4Py can be installed on Python 3.7.x / 3.8.x / 3.9.x by doing:
`pip install -U pm4py`

## Change Log
We track all changes in our [*CHANGELOG*](https://github.com/pm4py/pm4py-core/blob/release/CHANGELOG.md) file.

## Third Party Dependencies
As scientific library in the Python ecosystem, we rely on external libraries to offer our features.
In the */third_party* folder, we list all the licenses of our direct dependencies.
Please check the */third_party/LICENSES_TRANSITIVE* file to get a full list of all transitive dependencies and the corresponding license.

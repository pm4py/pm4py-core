# PM4Py
PM4Py is a python library that supports (state-of-the-art) process mining algorithms in python. It is completely open source and intended to be used in both academia and industry projects.
PM4Py is a product of the Fraunhofer Institute for Applied Information Technology.

## Documentation / API
The documentation about PM4Py is offered at http://pm4py.org/

## First Example
A very simple example, to whet your appetite:

```python
import pm4py

log = pm4py.read_xes('<path-to-xes-log-file.xes>')

net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log)

pm4py.view_petri_net(pnet, initial_marking, final_marking, format="svg")
```

## Installation
PM4Py can be installed on Python 3.6.x / 3.7.x / 3.8.x by doing:
`pip install -U pm4py`

## Release Notes
To track the incremental updates, we offer a [*RELEASE_NOTES*](https://github.com/pm4py/pm4py-core/blob/release/RELEASE_NOTES) file.

## Third Party Dependencies
As scientific library in the Python ecosystem, we rely on external libraries to offer our features.
Please check the [*README.THIRD_PARTY.md*](https://github.com/pm4py/pm4py-core/blob/release/README.THIRD_PARTY.md) file in order to know the dependencies and their license.

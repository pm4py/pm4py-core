# pm4py
pm4py is a python library that supports (state-of-the-art) process mining algorithms in python. 
It is open source (licensed under GPL) and intended to be used in both academia and industry projects.
pm4py is a product of the Fraunhofer Institute for Applied Information Technology.

## Documentation / API
The full documentation of pm4py can be found at http://pm4py.org/

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
pm4py can be installed on Python 3.7.x / 3.8.x / 3.9.x / 3.10.x by invoking:
*pip install -U pm4py*

## Release Notes
To track the incremental updates, please refer to the *CHANGELOG* file.

## Third Party Dependencies
As scientific library in the Python ecosystem, we rely on external libraries to offer our features.
In the */third_party* folder, we list all the licenses of our direct dependencies.
Please check the */third_party/LICENSES_TRANSITIVE* file to get a full list of all transitive dependencies and the corresponding license.

## Citing pm4py
If you are using pm4py in your scientific work, please cite pm4py as follows:

Berti, A., van Zelst, S.J., van der Aalst, W.M.P. (2019): Process Mining for Python (PM4Py): Bridging the Gap Between Process-and Data Science. In: Proceedings of the ICPM Demo Track 2019, co-located with 1st International Conference on Process Mining (ICPM 2019), Aachen, Germany, June 24-26, 2019. pp. 13-16 (2019). http://ceur-ws.org/Vol-2374/

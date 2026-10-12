# PM4Py

PM4Py is a python library that supports state-of-the-art process mining algorithms in Python.
It is open source and intended to be used in both academia and industry projects.

PM4Py is managed and developed by PIS — Process Intelligence Solutions (https://processintelligence.solutions/),
a spin-off from the Fraunhofer Institute for Applied Information Technology FIT where PM4Py was initially developed.

## Licensing

The open-source version of PM4Py, available on GitHub (https://github.com/process-intelligence-solutions/pm4py), is licensed under the GNU Affero General Public License version
3 (**AGPL-3.0**).

We offer a separate version of PM4Py for **commercial use in closed-source environments** under a different license. For
more information about the licensing options for using PM4Py in closed-source settings, please
visit https://processintelligence.solutions/pm4py#licensing.

## Documentation / API

The documentation of PM4Py can be found at https://processintelligence.solutions/pm4py/.

## First Example

Here is a simple example to spark your interest:

```python
import pm4py

if __name__ == "__main__":
    log = pm4py.read_xes('<path-to-xes-log-file.xes>')
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log)
    pm4py.view_petri_net(net, initial_marking, final_marking, format="svg")
```

## Installation
PM4Py can be installed on Python 3.9.x / 3.10.x / 3.11.x / 3.12.x / 3.13.x / 3.14.x by invoking:

`pip install -U pm4py`

Optional features can be installed through extras. For example:

`pip install -U "pm4py[polars,ml]"`

Use `pip install -U "pm4py[all]"` to install every optional feature supported on the current platform.

For a reproducible installation using the exact dependency versions validated by the project, use:

`pip install -U "pm4py[stable]"`

PM4Py is also running on older Python environments with different requirements sets, including:

- Python 3.8 (3.8.10): `third_party/old_python_deps/requirements_py38.txt`

## Requirements

The default installation contains the dependencies needed for mainstream usage. Additional integrations are grouped by
feature in `pyproject.toml`:

* `calendars`: workalendar
* `connectors`: requests
* `llm`: openai and requests
* `ml`: pyemd and scikit-learn
* `ocel`: jsonschema and pyarrow
* `polars`: Polars dataframe support
* `solvers`: cvxopt
* `stable`: the exact dependency versions validated by the project and used by CI
* `visualization`: pyvis
* `windows`: pygetwindow, pynput, and pywin32 (Windows only)

For a source checkout, install the project with `python -m pip install -e .`. Build, CI, and lint dependencies are
standard dependency groups and can be installed with, for example, `python -m pip install --group lint`.

Polars integration supports 1.40.1 and 2.x. Joins used in filtering and enrichment preserve event
order, including when lazy queries use the streaming engine (the default in Polars 2.0).

For optional PuLP support, PM4Py selects the backend for the installed PuLP version (3.x or 4.x).
PuLP 4 requires CBC to be installed separately: use `python -m pip install 'pulp[cbc]'` or put `cbc` on `PATH`.
SciPy remains the default LP solver.

## Release Notes

To track the incremental updates, please refer to the `CHANGELOG.md` file.

## Contributing

If you want to contribute to PM4Py, please review the [contributing guidelines and Contributor License Agreement (CLA)](https://processintelligence.solutions/pm4py/contributing).

## Third Party Dependencies

As scientific library in the Python ecosystem, we rely on external libraries to offer our features.
In the `/third_party` folder, we list all the licenses of our direct dependencies.
Please check the `/third_party/LICENSES_TRANSITIVE` file to get a full list of all transitive dependencies and the
corresponding license.

## Citing PM4Py

If you are using PM4Py in your scientific work, please cite PM4Py as follows:

> **Alessandro Berti, Sebastiaan van Zelst, Daniel Schuster**. (2023). *PM4Py: A process mining library for Python*.
> Software Impacts, 17, 100556. doi: 10.1016/j.simpa.2023.100556

[DOI](https://doi.org/10.1016/j.simpa.2023.100556) | [Article Link](https://www.sciencedirect.com/science/article/pii/S2665963823000933)

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

## Legal Notice

This repository is managed by Process Intelligence Solutions (PIS). Further information about PIS can be found online
at https://processintelligence.solutions.

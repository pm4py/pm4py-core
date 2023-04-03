# A dcr implementation in pm4py

Tested and working with python 3.11.0

Create a python virtual environment and: 
```
pip install -r requirements.txt
```

Check out and run the jupyter notebook from notebooks/pm4py_dcr_example.ipynb


The running example is on the sepsis event log.

## From pm4py:

## Installation
pm4py can be installed on Python 3.8.x / 3.9.x / 3.10.x / 3.11.x by invoking:
*pip install -U pm4py*

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
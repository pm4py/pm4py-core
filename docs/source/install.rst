Installation
============

pip
---

To use ``pm4py`` on any OS, install it using ``pip``:

.. code-block:: console

   (.venv) $ pip install pm4py

``pmp4y`` uses the ``Graphviz`` library for rendering visualizations.
Please install `Graphviz <https://graphviz.org/download/>`_.

After installation, GraphViz is located in the ``program files`` directory.
The ``bin\`` folder of the GraphViz directory needs to be added manually to the ``system path``.
In order to do so, please follow `this instruction <https://stackoverflow.com/questions/44272416/how-to-add-a-folder-to-path-environment-variable-in-windows-10-with-screensho>`_.

Docker
------
To install pm4py via Docker, use:

.. code-block:: console

   $ docker pull pm4py/pm4py-core:latest

To run pm4py via docker, use:

.. code-block:: console

   $ docker run -it pm4py/pm4py-core:latest bash
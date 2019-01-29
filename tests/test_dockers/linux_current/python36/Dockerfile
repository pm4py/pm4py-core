FROM python:3.6

RUN apt-get update
RUN apt-get -y install nano vim
RUN apt-get -y install git
RUN apt-get -y install python3-pydot python-pydot python-pydot-ng graphviz
RUN apt-get -y install python3-tk
RUN apt-get -y install zip unzip
RUN wget https://github.com/pm4py/pm4py-source/archive/develop.zip
RUN unzip develop.zip
RUN cd pm4py-source-develop && pip install -r requirements_stable.txt && cp tests/test_dockers/setups/setup_develop.py setup.py && python setup.py install

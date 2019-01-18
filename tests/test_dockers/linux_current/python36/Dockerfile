FROM python:3.6

RUN apt-get update
RUN apt-get -y install nano vim
RUN apt-get -y install git
RUN apt-get -y install python3-pydot python-pydot python-pydot-ng graphviz
RUN apt-get -y install python3-tk
RUN apt-get -y install zip unzip
RUN pip install -U pm4py
RUN pip install -U jupyter
RUN wget https://github.com/pm4py/pm4py-source/archive/develop.zip
RUN unzip develop.zip
RUN cd pm4py-source-develop && pip install -U -r requirements.txt && pip install jupyter && python setup.py install

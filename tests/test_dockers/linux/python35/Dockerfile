FROM python:3.5

RUN apt-get update
RUN apt-get -y install nano vim
RUN apt-get -y install git
RUN apt-get -y install python3-pydot python-pydot python-pydot-ng graphviz
RUN apt-get -y install python3-tk
RUN apt-get -y install zip unzip
RUN pip install -U pm4py
RUN wget https://github.com/pm4py/pm4py-source/archive/master.zip
RUN unzip master.zip
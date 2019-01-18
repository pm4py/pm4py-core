FROM python:3.6
#FROM tiangolo/uwsgi-nginx-flask:python3.6

RUN apt-get update
RUN apt-get -y install nano vim
RUN apt-get -y install git
RUN apt-get -y install python3-pydot python-pydot python-pydot-ng graphviz
RUN apt-get -y install python3-tk
RUN apt-get -y install zip unzip
RUN pip install -U lxml
RUN pip install -U graphviz
RUN pip install -U ciso8601
RUN pip install -U numpy
RUN pip install -U scipy
RUN pip install -U pandas
RUN pip install -U dataclasses
RUN pip install -U cvxopt
RUN pip install -U flask
RUN pip install -U flask-cors
RUN pip install -U matplotlib
RUN pip install -U networkx==1.11
RUN pip install -U sklearn
RUN pip install -U jupyter

COPY . /app

#ENTRYPOINT ["uwsgi", "--http", "0.0.0.0:80", "--module", "main:app", "--processes", "8", "--threads", "8"]

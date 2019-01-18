FROM python:3.6
#FROM tiangolo/uwsgi-nginx-flask:python3.6

RUN apt-get update
RUN apt-get -y install nano vim
RUN apt-get -y install git
RUN apt-get -y install python3-pydot python-pydot python-pydot-ng graphviz
RUN apt-get -y install python3-tk
RUN apt-get -y install zip unzip
RUN pip install pyvis==0.1.5.0
RUN pip install networkx==2.2
RUN pip install matplotlib==2.2.2
RUN pip install numpy==1.16.0
RUN pip install ciso8601==2.1.1
RUN pip install cvxopt==1.2.2
RUN pip install dataclasses==0.6
RUN pip install lxml==4.3.0
RUN pip install graphviz==0.10.1
RUN pip install pandas==0.23.4
RUN pip install scipy==1.2.0
RUN pip install scikit-learn==0.20.2

COPY . /app

#ENTRYPOINT ["uwsgi", "--http", "0.0.0.0:80", "--module", "main:app", "--processes", "8", "--threads", "8"]

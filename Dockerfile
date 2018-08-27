FROM python:3.6

RUN apt-get update
RUN apt-get -y install nano vim
RUN apt-get -y install git
RUN pip install lxml
RUN pip install graphviz
RUN pip install ciso8601
RUN pip install pandas
RUN pip install dataclasses
RUN pip install cvxopt
RUN pip install flask
RUN pip install flask-cors

COPY . /app

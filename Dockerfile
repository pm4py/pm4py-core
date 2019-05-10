FROM python:3.6

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install nano vim
RUN apt-get -y install git
RUN apt-get -y install python3-pydot python-pydot python-pydot-ng graphviz
RUN apt-get -y install python3-tk
RUN apt-get -y install zip unzip
RUN pip install pyvis networkx==2.2 matplotlib==2.2.2 numpy ciso8601 pyarrow cvxopt lxml graphviz pandas scipy scikit-learn pytz==2018.9
RUN pip install pydotplus

RUN pip install pulp intervaltree
COPY . /app
RUN cd /app && cp tests/test_dockers/setups/setup_master.py setup.py && python setup.py install

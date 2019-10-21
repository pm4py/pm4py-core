FROM python:3.6

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install nano vim
RUN apt-get -y install git
RUN apt-get -y install python3-pydot python-pydot python-pydot-ng graphviz
RUN apt-get -y install python3-tk
RUN apt-get -y install zip unzip
RUN pip install pyvis==0.1.7.0 networkx==2.4 matplotlib==3.1.1 numpy==1.17.3 ciso8601==2.1.2 pyarrow==0.13.0 lxml==4.4.1 graphviz==0.13 pandas==0.25.2 scipy==1.3.1 scikit-learn==0.21.3 pytz==2019.3
RUN pip install pydotplus==2.0.2

RUN pip install pulp==1.6.10 ortools==7.4.7247 prefixspan==0.5.2 fasttext==0.9.1 pybind11==2.4.3 intervaltree==3.0.2
COPY . /app
RUN cd /app && cp tests/test_dockers/setups/setup_master.py setup.py && python setup.py install

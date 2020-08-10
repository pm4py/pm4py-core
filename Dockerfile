FROM python:3.7

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install nano vim
RUN apt-get -y install git
RUN apt-get -y install python3-pydot python-pydot python-pydot-ng graphviz
RUN apt-get -y install python3-tk
RUN apt-get -y install zip unzip
RUN apt-get -y install gcc gfortran python-dev libopenblas-dev liblapack-dev cython
RUN apt-get -y install g++ libboost-all-dev libncurses5-dev wget
RUN apt-get -y install libtool flex bison pkg-config g++ libssl-dev automake
RUN apt-get -y install libjemalloc-dev libboost-dev libboost-filesystem-dev libboost-system-dev libboost-regex-dev python3-dev autoconf flex bison cmake
RUN apt-get -y install libxml2-dev libxslt-dev libfreetype6-dev libsuitesparse-dev
RUN pip install -U wheel six pytest
RUN pip install cython==0.29.21 pyvis==0.1.8.2 networkx==2.4 matplotlib==3.3.0 numpy==1.19.1 lxml==4.5.2 graphviz==0.14 pyarrow==0.15.1 pandas==1.1.0 scipy==1.5.2 pydotplus==2.0.2 scikit-learn==0.23.2 pulp==2.1 pytz==2020.1 intervaltree==3.1.0 jsonpickle==1.4.1 stringdist deprecation tqdm pyemd==0.5.1
COPY . /app
RUN cd /app && cp tests/test_dockers/setups/setup_master.py setup.py && python setup.py install

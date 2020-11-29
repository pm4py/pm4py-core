FROM python:3.8

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
RUN pip install MarkupSafe==1.1.1 backcall==0.2.0 certifi==2020.11.8 colorama==0.4.3 decorator==4.4.2 ipython-genutils==0.2.0 joblib==0.17.0 more-itertools==8.6.0 mpmath==1.1.0 numpy==1.19.3 parso==0.8.0 pickleshare==0.7.5 Pillow==8.0.1 Pygments==2.7.2 pyparsing==2.4.7 pytz==2020.4 setuptools==50.3.2 six==1.15.0 sortedcontainers==2.3.0 threadpoolctl==2.1.0 wcwidth==0.2.5 cycler==0.10.0 jedi==0.17.2 jinja2==2.11.2 kiwisolver==1.3.1 networkx==2.5 packaging==20.7 prompt-toolkit==3.0.7 python-dateutil==2.8.1 scipy==1.5.4 traitlets==5.0.5 zipp==3.4.0 importlib-metadata==3.1.0 ipython==7.19.0 jsonpickle==1.4.1 deprecation==2.1.0 graphviz==0.15 intervaltree==3.1.0 lxml==4.6.1 matplotlib==3.3.3 pandas==1.1.4 pulp==2.1 pydotplus==2.0.2 pyvis==0.1.8.2 scikit-learn==0.23.2 StringDist==1.0.9 sympy==1.6.2 cython==0.29.21 tqdm==4.54.0

COPY . /app
RUN cd /app && cp tests/test_dockers/setups/setup_master.py setup.py && python setup.py install

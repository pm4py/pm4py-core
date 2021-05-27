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
RUN pip install backcall==0.2.0 colorama==0.4.4 cycler==0.10.0 decorator==5.0.7 deprecation==2.1.0 graphviz==0.16 intervaltree==3.1.0 ipython==7.22.0 ipython-genutils==0.2.0 jedi==0.18.0 jinja2==3.0.0a1 joblib==1.0.1 jsonpickle==2.0.0 kiwisolver==1.3.1 lxml==4.6.3 MarkupSafe==2.0.0rc1 matplotlib==3.4.1 mpmath==1.2.1 networkx==2.5.1 numpy==1.20.2 packaging==20.9 pandas==1.2.4 parso==0.8.2 pickleshare==0.7.5 pillow==8.2.0 prompt-toolkit==3.0.18 pulp==2.1 pydotplus==2.0.2 pygments==2.8.1 pyparsing==3.0.0b2 python-dateutil==2.8.1 pytz==2021.1 pyvis==0.1.9 scikit-learn==0.24.1 scipy==1.6.2 setuptools==56.0.0 six==1.15.0 sortedcontainers==2.3.0 stringdist==1.0.9 sympy==1.8 threadpoolctl==2.1.0 tqdm==4.60.0 traitlets==5.0.5 wcwidth==0.2.5
RUN pip install backcall==0.2.0 colorama==0.4.4 cycler==0.10.0 deprecation==2.1.0 graphviz==0.16 intervaltree==3.1.0 ipython==7.22.0 ipython-genutils==0.2.0 jedi==0.18.0 jinja2==3.0.0a1 joblib==1.0.1 jsonpickle==2.0.0 kiwisolver==1.3.1 lxml==4.6.3 MarkupSafe==2.0.0rc1 matplotlib==3.4.1 mpmath==1.2.1 networkx==2.5.1 numpy==1.20.2 packaging==20.9 pandas==1.2.4 parso==0.8.2 pickleshare==0.7.5 pillow==8.2.0 prompt-toolkit==3.0.18 pulp==2.1 pydotplus==2.0.2 pygments==2.8.1 pyparsing==3.0.0b2 python-dateutil==2.8.1 pytz==2021.1 pyvis==0.1.9 scikit-learn==0.24.1 scipy==1.6.2 setuptools==56.0.0 six==1.15.0 sortedcontainers==2.3.0 stringdist==1.0.9 sympy==1.8 threadpoolctl==2.1.0 tqdm==4.60.0 traitlets==5.0.5 wcwidth==0.2.5

COPY . /app
RUN cd /app && cp tests/test_dockers/setups/setup_master.py setup.py && python setup.py install
RUN cd /app && python setup.py install

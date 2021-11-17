FROM python:3.9

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install nano vim
RUN apt-get -y install git
RUN apt-get -y install python3-pydot graphviz
RUN apt-get -y install python3-tk
RUN apt-get -y install zip unzip
RUN apt-get -y install gcc gfortran python-dev libopenblas-dev liblapack-dev
RUN apt-get -y install g++ libboost-all-dev libncurses5-dev wget
RUN apt-get -y install libtool flex bison pkg-config g++ libssl-dev automake
RUN apt-get -y install libjemalloc-dev libboost-dev libboost-filesystem-dev libboost-system-dev libboost-regex-dev python3-dev autoconf flex bison cmake
RUN apt-get -y install libxml2-dev libxslt-dev libfreetype6-dev libsuitesparse-dev
RUN pip install -U wheel six pytest
RUN pip install backcall==0.2.0 colorama==0.4.4 cycler==0.11.0 decorator==5.1.0 deprecation==2.1.0 graphviz==0.18.2 intervaltree==3.1.0 ipython==7.29.0 jedi==0.18.1 jinja2==3.0.3 joblib==1.1.0 jsonpickle==2.0.0 kiwisolver==1.3.2 lxml==4.6.4 MarkupSafe==2.0.1 matplotlib==3.5.0 matplotlib-inline==0.1.3 mpmath==1.2.1 networkx==2.6.3 numpy==1.21.4 packaging==21.2 pandas==1.3.4 parso==0.8.2 pickleshare==0.7.5 pillow==8.4.0 prompt-toolkit==3.0.22 pulp==2.5.1 pydotplus==2.0.2 pygments==2.10.0 pyparsing==3.0.6 python-dateutil==2.8.2 pytz==2021.3 pyvis==0.1.9 scikit-learn==1.0.1 scipy==1.7.2 setuptools==59.1.1 six==1.16.0 sortedcontainers==2.4.0 stringdist==1.0.9 sympy==1.9 threadpoolctl==3.0.0 tqdm==4.62.3 traitlets==5.1.1 wcwidth==0.2.5 

COPY . /app
RUN cd /app && python setup.py install

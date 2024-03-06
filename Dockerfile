FROM python:3.12.2

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install nano vim
RUN apt-get -y install git
RUN apt-get -y install python3-pydot graphviz
RUN apt-get -y install python3-tk
RUN apt-get -y install zip unzip
RUN apt-get -y install gcc gfortran libopenblas-dev liblapack-dev
RUN apt-get -y install g++ libboost-all-dev libncurses5-dev wget
RUN apt-get -y install libtool flex bison pkg-config g++ libssl-dev automake
RUN apt-get -y install libjemalloc-dev libboost-dev libboost-filesystem-dev libboost-system-dev libboost-regex-dev python3-dev autoconf flex bison cmake
RUN apt-get -y install libxml2-dev libxslt-dev libfreetype6-dev libsuitesparse-dev
RUN pip install -U wheel six pytest
RUN pip install colorama==0.4.6 contourpy==1.2.0 cycler==0.12.1 deprecation==2.1.0 fonttools==4.49.0 graphviz==0.20.1 intervaltree==3.1.0 kiwisolver==1.4.5 lxml==5.1.0 matplotlib==3.8.3 networkx==3.2.1 numpy==1.26.4 packaging==23.2 pandas==2.2.1 pillow==10.2.0 pydotplus==2.0.2 pyparsing==3.1.1 python-dateutil==2.9.0.post0 pytz==2024.1 scipy==1.12.0 six==1.16.0 sortedcontainers==2.4.0 tqdm==4.66.2 tzdata==2024.1

COPY . /app
RUN cd /app && python setup.py install

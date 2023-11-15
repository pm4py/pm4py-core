FROM python:3.11.6

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
RUN pip install colorama==0.4.6 contourpy==1.2.0 cycler==0.12.1 deprecation==2.1.0 fonttools==4.44.1 graphviz==0.20.1 intervaltree==3.1.0 kiwisolver==1.4.5 lxml==4.9.3 matplotlib==3.8.1 networkx==3.2.1 numpy==1.26.2 packaging==23.2 pandas==2.1.3 Pillow==10.1.0 pydotplus==2.0.2 pyparsing==3.1.1 python-dateutil==2.8.2 pytz==2023.3.post1 scipy==1.11.3 six==1.16.0 sortedcontainers==2.4.0 StringDist==1.0.9 tqdm==4.66.1 tzdata==2023.3 

COPY . /app
RUN cd /app && python setup.py install

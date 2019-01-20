cd python35
docker build --no-cache -t testdockerlinuxpython35master .
docker run testdockerlinuxpython35master bash -c "cd pm4py-source-master/tests && python execute_tests.py"
docker run testdockerlinuxpython35master bash -c "python -c \"import pm4py ; print(pm4py.__version__)\""
cd ..
cd python37
docker build --no-cache -t testdockerlinuxpython37master .
docker run testdockerlinuxpython37master bash -c "cd pm4py-source-master/tests && python execute_tests.py"
docker run testdockerlinuxpython37master bash -c "python -c \"import pm4py ; print(pm4py.__version__)\""
cd ..
cd python36
docker build --no-cache -t testdockerlinuxpython36master .
docker run testdockerlinuxpython36master bash -c "cd pm4py-source-master/tests && python execute_tests.py"
docker run testdockerlinuxpython36master bash -c "python -c \"import pm4py ; print(pm4py.__version__)\""

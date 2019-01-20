cd python35
docker build --no-cache -t testdockerlinuxpython35 .
docker run testdockerlinuxpython35 bash -c "cd pm4py-source-master/tests && python execute_tests.py"
docker run testdockerlinuxpython35 bash -c "python -c \"import pm4py ; print(pm4py.__version__)\""
cd ..
cd python37
docker build --no-cache -t testdockerlinuxpython37 .
docker run testdockerlinuxpython37 bash -c "cd pm4py-source-master/tests && python execute_tests.py"
docker run testdockerlinuxpython37 bash -c "python -c \"import pm4py ; print(pm4py.__version__)\""
cd ..
cd python36
docker build --no-cache -t testdockerlinuxpython36 .
docker run testdockerlinuxpython36 bash -c "cd pm4py-source-master/tests && python execute_tests.py"
docker run testdockerlinuxpython36 bash -c "python -c \"import pm4py ; print(pm4py.__version__)\""


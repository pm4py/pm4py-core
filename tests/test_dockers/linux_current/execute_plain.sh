cd python35
docker build --no-cache -t testdockerlinuxpython35develop .
docker run testdockerlinuxpython35develop bash -c "cd pm4py-source-develop/tests && python execute_tests.py"
docker run testdockerlinuxpython35develop bash -c "python -c \"import pm4py ; print(pm4py.__version__)\""
cd ..
cd python37
docker build --no-cache -t testdockerlinuxpython37develop .
docker run testdockerlinuxpython37develop bash -c "cd pm4py-source-develop/tests && python execute_tests.py"
docker run testdockerlinuxpython37develop bash -c "python -c \"import pm4py ; print(pm4py.__version__)\""
cd ..
cd python36
docker build --no-cache -t testdockerlinuxpython36develop .
docker run testdockerlinuxpython36develop bash -c "cd pm4py-source-develop/tests && python execute_tests.py"
docker run testdockerlinuxpython36develop bash -c "python -c \"import pm4py ; print(pm4py.__version__)\""

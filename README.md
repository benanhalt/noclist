# noclist
This repository contains a solution to the
https://homework.adhoc.team/noclist/ homework problem. It provides a
commandline program that retrieves a list of user ids from a BADSEC
server and prints the result as a JSON list to stdout. The program
exits with status code 0 on success and code 1 on failure. Requests to
the server are attempted up to three times before failure.

The solution is implemented in the `noclist.py` Python script which
can be run by setting up a Python virtualenv with the dependencies
recorded in the `requirements.txt` file. It has been tested with
Python 3.11.

```
python -m venv ve
source ve/bin/activate
pip install -r requirements.txt
```

If the test BADSEC server is started as specified in the problem

```
docker run --rm -p 8888:8888 adhocteam/noclist
```

then the `noclist.py` program can be invoked as 

```
python noclist.py http://localhost:8888
```

Passing a `-v` flag will enable verbose logging to stderr. The base
url can be changed to operate with alternate BADSEC servers.

## Tests
Tests are implemented in `tests.py` and can be invoked as

```
python tests.py
```

If the test server is running, a basic integration test can be enabled
by including the test server url as an environment variable.

```
NOCLIST_TEST_SERVER=http://localhost:8888 python tests.py 
```

The source code includes types which can be checked using `mypy`.

```
mypy noclist.py tests.py
```

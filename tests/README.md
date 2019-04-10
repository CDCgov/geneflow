# Run BDD Tests

Use the folloiwng steps to run unit tests:

1. If GeneFlow is not installed as a python package, initialize your PYTHONPATH environment variable.

2. Initialize the database:

```
geneflow init-db -c ./test.conf -e local
```

3. Update behave.ini based on your environment.

4. Run the unit tests (you may need to install the testing framework with "pip3 install behave"):

```
behave
```


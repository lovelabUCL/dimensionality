# running a Python test
test:
	cd ./Python/FunctionalDimensionality/; PYTHONPATH=. coverage run tests/test_funcdim.py
	cd ./Python/FunctionalDimensionality/; PYTHONPATH=. coverage run tests/test_crossval.py

build:
	virtualenv venv && source venv/bin/activate && python setup.py sdist bdist_wheel
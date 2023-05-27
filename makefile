SHELL=/bin/bash

build:
	virtualenv venv && source venv/bin/activate && python setup.py sdist bdist_wheel

clean:
	rm -Rf dist build replicator_cli.egg-info venv

publish: clean build
	virtualenv venv && source venv/bin/activate && pip install twine && twine upload dist/*
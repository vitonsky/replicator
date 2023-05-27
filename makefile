build:
	virtualenv venv && source venv/bin/activate && python setup.py sdist bdist_wheel

clean:
	rm -Rf dist build replicator_cli.egg-info

publish: clean build
	virtualenv venv && source venv/bin/activate && twine upload dist/*
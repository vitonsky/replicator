from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
    
setup(
    name = 'replicator-cli',
    version = '0.0.2',
    author = 'Robert Vitonsky',
    author_email = 'rob@vitonsky.net',
    license = 'MIT',
    description = 'Task runner for backups',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/vitonsky/replicator',
    py_modules = ['replicator', 'app'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        replicator=app:cli
    '''
)
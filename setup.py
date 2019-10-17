from setuptools import setup
from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

pfile = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pfile['packages'], r=False)
test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)


setup(
    name='py_proxy',
    version='0.1',
    packages=['py_proxy'],
    test_suite='testsuite',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'py_proxy=py_proxy.cli:main'
        ]
    },
    setup_requires=[
        'flake8',
        'wheel',
        'pipenv'
    ],
    zip_safe=True,
    tests_require=test_requirements,
    python_requires='>=3.7'
)

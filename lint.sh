#! /bin/bash

set -e
. ./activate.sh
echo Running isort
isort src tests
echo Running black.
black src tests
echo Running flake8
flake8 src tests
echo Running pylint src
pylint src
echo Running pylint tests
pylint tests  # seperate or crash happens in git-bash
echo Running mypy
mypy src tests
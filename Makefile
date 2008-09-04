#
# Makefile for pymills
# ~~~~~~~~~~~~~~~~~~~~

PYTHON ?= python

export PATH=$(shell echo "$$HOME/bin:$$PATH")

export PYTHONPATH=$(shell echo "$$PYTHONPATH"):$(shell python -c 'import os; print ":".join(os.path.abspath(line.strip()) for line in file("PYTHONPATH"))' 2>/dev/null)

.PHONY: all clean clean-pyc codetags pyflakes test

all: clean-pyc pyflakes test

clean: clean-pyc
	rm -rf build dist pymills.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

codetags:
	@find_codetags.py

pyflakes:
	@find . -name "*.py" -exec pyflakes {} +

test:
	@nosetests

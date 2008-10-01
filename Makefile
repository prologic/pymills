#
# Makefile for pymills
# ~~~~~~~~~~~~~~~~~~~~

.PHONY: all clean todo lint test graph

all: clean lint test graph

clean:
	@rm -rf build dist pymills.egg-info
	@find . -name '*.pyc' -delete
	@find . -name '*.pyo' -delete
	@find . -name '*~' -delete

lint:
	@find . -name "*.py" -exec pyflakes {} +

test:
	@nosetests

graph:
	@sfood pymills -i -I tests -d -u 2> /dev/null | sfood-graph | dot -Tps | ps2pdf - > pymills.pdf

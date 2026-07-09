.PHONY: all clean test run

PYTHON := python
PYTEST := $(PYTHON) -m pytest

all:

run:
	$(PYTHON) -m src.main $(ARGS)

test:
	$(PYTEST) tests/ -v

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

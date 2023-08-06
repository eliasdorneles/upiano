.DEFAULT_GOAL := help

format:  ## Format code
	isort --sl .
	black .

# Implements this pattern for autodocumenting Makefiles:
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
#
# Picks up all comments that start with a ## and are at the end of a target definition line.
.PHONY: help
help:  ## Display command usage
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


release: dist ## package and upload a release
	twine upload --repository upiano --verbose dist/*

dist: clean ## builds source and wheel package
	poetry build
	ls -l dist

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache


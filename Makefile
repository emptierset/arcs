.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")
SRC_DIRECTORIES := arcsync/ tests/

## help: Show the help.
.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


## show: Show the current environment.
.PHONY: show
show:
	@echo "Current environment:"
	@echo "Running using $(ENV_PREFIX)"
	@$(ENV_PREFIX)python -V
	@$(ENV_PREFIX)python -m site

## doc: Clean generated docs and compile fresh ones.
.PHONY: doc
doc:
	$(MAKE) -C docs/ clean
	$(MAKE) -C docs/ html

## black: Format code using black.
.PHONY: black
black:
	$(ENV_PREFIX)black -l 99 --preview --enable-unstable-feature=string_processing $(SRC_DIRECTORIES) mypy_stubs/

## blackcheckonly: Check code format using black.
.PHONY: blackcheckonly
blackcheckonly:
	$(ENV_PREFIX)black -l 99 --check $(SRC_DIRECTORIES)

## isort: Format code using isort.
.PHONY: isort
isort:
	$(ENV_PREFIX)isort --line-length 99 --profile black $(SRC_DIRECTORIES)

## autoflake: Remove unused imports using autoflake.
.PHONY: autoflake
autoflake:
	$(ENV_PREFIX)autoflake -ri $(SRC_DIRECTORIES)

## autoflakeall: Remove all unused imports using autoflake.
.PHONY: autoflakeall
autoflakeall:
	$(ENV_PREFIX)autoflake --remove-all-unused-imports -ri $(SRC_DIRECTORIES)

## fmt: Format code using isort, black, and autoflake.
.PHONY: fmt
fmt: isort black autoflake

## flake: Run flake8 linter.
.PHONY: flake
flake:
	$(ENV_PREFIX)flake8 --extend-ignore=E203,F401 --max-line-length 99 $(SRC_DIRECTORIES)

## lint: Run pep8 linter and black checker.
.PHONY: lint
lint: flake blackcheckonly

## mypy: Run mypy type checker.
.PHONY: mypy
mypy:
	$(ENV_PREFIX)mypy --strict $(SRC_DIRECTORIES)

## check: Run all linters and mypy.
.PHONY: check
check: lint mypy

## cov: Run tests and produce coverage reports if successful.
.PHONY: cov
cov:
	@if $(ENV_PREFIX)pytest -vv --cov-config .coveragerc --cov-report term-missing --cov=arcsync -l --tb=short --maxfail=1 tests/; \
	then \
		:; \
	else \
		exit $?; \
	fi
	$(ENV_PREFIX)coverage xml
	$(ENV_PREFIX)coverage html

# TODO(cleanup): The output of this is a bit ugly when you have a ton of tests. Maybe check the
# flags and see what we can fiddle with.
## test: Run tests and generate coverage report.
.PHONY: test
test:
	$(ENV_PREFIX)pytest -vv	-l --tb=short tests/

## proofnofmt: ("Proofread") Run all linters, mypy, and unit tests, without fmt.
.PHONY: proofnofmt
proofnofmt: check cov

## proof: ("Proofread") Run all linters, mypy, and unit tests.
.PHONY: proof
proof: fmt check cov

## watch: Run tests on every change.
.PHONY: watch
watch:
	ls **/**.py | entr $(ENV_PREFIX)pytest -s -vvv -l --tb=long tests/

## clean: Clean unused files.
.PHONY: clean
clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/

## init: Initialize the project based on an application template.
.PHONY: init
init:
	@./.github/init.sh

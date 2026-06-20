.PHONY: build check lint mutation-test static-check test verify

override REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

check: static-check mutation-test

verify: check

lint: static-check

test: mutation-test

build: static-check

static-check:
	python3 "$(REPO_ROOT)/scripts/check-baseline.py"

mutation-test:
	cd "$(REPO_ROOT)" && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v

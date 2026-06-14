.PHONY: build check lint static-check test verify

override REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

check: static-check

verify: check

lint: static-check

test: static-check

build: static-check

static-check:
	python3 "$(REPO_ROOT)/scripts/check-baseline.py"

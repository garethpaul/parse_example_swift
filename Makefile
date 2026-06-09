.PHONY: build check lint static-check test verify

check: static-check

verify: check

lint: static-check

test: static-check

build: static-check

static-check:
	python3 scripts/check-baseline.py

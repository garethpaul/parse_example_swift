.PHONY: build check integrity-check lint mutation-test static-check test verify

override REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

check: static-check mutation-test

verify: check

lint: static-check

test: mutation-test

build: static-check

integrity-check:
	@expected=$$(sed -n 's/^  INTEGRITY_SHA256: //p' "$(REPO_ROOT)/.github/workflows/check.yml"); \
	actual=$$(python3 -c 'import hashlib, sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' "$(REPO_ROOT)/scripts/check-integrity.py"); \
	if [ "$$actual" != "$$expected" ]; then \
		echo "integrity bootstrap digest mismatch" >&2; \
		exit 1; \
	fi
	python3 "$(REPO_ROOT)/scripts/check-integrity.py"

static-check: integrity-check
	python3 "$(REPO_ROOT)/scripts/check-baseline.py"

mutation-test:
	cd "$(REPO_ROOT)" && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v

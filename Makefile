ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override REPO_ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); directory=$$(/usr/bin/dirname -- "$$path"); CDPATH= cd -- "$$directory" && /bin/pwd -P)
override SHELL_REPO_ROOT := '$(subst ','"'"',$(REPO_ROOT))'

.PHONY: build check integrity-check lint mutation-test root-test static-check test verify

check: static-check mutation-test root-test

verify: check

lint: static-check

test: mutation-test

build: static-check

integrity-check:
	@expected=$$(sed -n 's/^  INTEGRITY_SHA256: //p' $(SHELL_REPO_ROOT)/.github/workflows/check.yml); \
	actual=$$(python3 -c 'import hashlib, sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' $(SHELL_REPO_ROOT)/scripts/check-integrity.py); \
	if [ "$$actual" != "$$expected" ]; then \
		echo "integrity bootstrap digest mismatch" >&2; \
		exit 1; \
	fi
	python3 $(SHELL_REPO_ROOT)/scripts/check-integrity.py

static-check: integrity-check
	python3 $(SHELL_REPO_ROOT)/scripts/check-baseline.py

mutation-test:
	cd $(SHELL_REPO_ROOT) && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v

root-test:
	PYTHONDONTWRITEBYTECODE=1 python3 $(SHELL_REPO_ROOT)/scripts/test-makefile-root.py

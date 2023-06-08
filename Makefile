PACKAGE = mixer

# ==============
#  Developemnt
# ==============

VIRTUAL_ENV ?= $(CURDIR)/.venv
$(VIRTUAL_ENV): poetry.lock
	@poetry install --with dev,tests
	@poetry run pre-commit install --hook-type pre-push
	@touch $(VIRTUAL_ENV)

.PHONY: test t
test t: $(VIRTUAL_ENV)
	@poetry run pytest tests

.PHONY: lint
lint: $(VIRTUAL_ENV)
	@poetry run mypy $(PACKAGE)
	@poetry run ruff $(PACKAGE)

.PHONY: doc
# target: doc - Compile the docs
doc: docs
	@poetry run sphinx-build --source-dir=docs/ --build-dir=docs/_build --all-files


# ==============
#  Bump version
# ==============

.PHONY: release
VPART?=minor
# target: release - Bump version
release: $(VIRTUAL_ENV)
	git checkout develop
	git pull
	git checkout master
	git merge develop
	git pull
	@poetry version $(VPART)
	git commit -am "Bump version: `poetry version -s`"
	git tag `poetry version -s`
	git checkout develop
	git merge master

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release VPART=patch

.PHONY: major
major:
	make release VPART=major

.PHONY: version v
version v:
	@poetry version -s

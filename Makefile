MODULE=mixer
SPHINXBUILD=sphinx-build
ALLSPHINXOPTS= -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
BUILDDIR=_build

all: $(VIRTUAL_ENV)

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile

.PHONY: clean
# target: clean - Clean repo
clean:
	@rm -rf build dist docs/_build
	find $(CURDIR)/$(MODULE) -name "*.pyc" -delete
	find $(CURDIR)/$(MODULE) -name "*.orig" -delete
	find $(CURDIR)/$(MODULE) -name "__pycache__" -delete


# ==============
#  Bump version
# ==============

.PHONY: release
VERSION?=minor
# target: release - Bump version
release:
	@pip install bump2version
	@bump2version $(VERSION)
	@git checkout master
	@git merge develop
	@git checkout develop
	@git push origin master develop
	@git push --tags

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release VERSION=patch


# ===============
#  Build package
# ===============

.PHONY: register
# target: register - Register module on PyPi
register:
	@python setup.py register

.PHONY: upload
# target: upload - Upload module on PyPi
upload: clean
	@pip install twine wheel
	@python setup.py sdist bdist_wheel
	@twine upload dist/*.whl || true
	@twine upload dist/*.gz || true

.PHONY: docs
# target: docs - Compile the docs
docs: docs
	@$(VIRTUAL_ENV)/bin/pip install sphinx
	python setup.py build_sphinx --source-dir=docs/ --build-dir=docs/_build --all-files
	# python setup.py upload_sphinx --upload-dir=docs/_build/html


# =============
#  Development
# =============

VIRTUAL_ENV 	?= $(CURDIR)/env
$(VIRTUAL_ENV): requirements.txt
	@[ -d $(VIRTUAL_ENV) ]	|| python -m venv $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install -r requirements.txt
	@touch $(VIRTUAL_ENV)

$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV) requirements-tests.txt
	@$(VIRTUAL_ENV)/bin/pip install -r requirements-tests.txt
	@touch $(VIRTUAL_ENV)/bin/py.test

TEST=tests
.PHONY: t
# target: t - Runs tests
t: clean $(VIRTUAL_ENV)/bin/py.test
	$(VIRTUAL_ENV)/bin/py.test $(TEST) -s

.PHONY: audit
# target: audit - Audit code
audit:
	@pylama $(MODULE) -i E501

.PHONY: serve
# target: serve - Run HTTP server with compiled docs
serve:
	pyserve docs/_build/html/

.PHONY: pep8
pep8:
	find $(MODULE) -name "*.py" | xargs -n 1 autopep8 -i

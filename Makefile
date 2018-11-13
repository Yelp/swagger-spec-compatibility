.PHONY: minimal development
minimal development: venv install-hooks
	@true

.PHONY: install-hooks
install-hooks: venv
	./venv/bin/pre-commit install -f --install-hooks

venv: requirements-dev.txt requirements-docs.txt setup.py tox.ini
	-deactivate
	rm -rf venv
	tox -e venv

.PHONY: test
test:
	tox

.PHONY: docs
docs:
	tox -e docs

.PHONY: clean
clean:
	find -name '*.pyc' -delete
	find -name '__pycache__' -delete
	rm -rf .tox venv docs/build

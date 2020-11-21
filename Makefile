clean:
	rm -rf dist build *.egg-info
	find . -name ".pyc" -delete

upload: clean
	python setup.py sdist bdist_wheel
	twine upload -u krukov dist/*

LENGTH=120

.PHONY: format
format: black isort

.PHONY: pylint
pylint:
	pylint amocrm/v2 --reports=n --max-line-length=$(LENGTH)

.PHONY: isort
isort:
	@echo -n "Run isort"
	isort -rc amocrm/v2 tests

.PHONY: black
black:
	@echo -n "Run black"
	black -l $(LENGTH) amocrm/v2 tests

.PHONY: check-isort
check-isort:
	isort --lines $(LENGTH) -vb -rc --check-only -df amocrm/v2 tests

.PHONY: check-styles
check-styles:
	pycodestyle amocrm/v2 tests --max-line-length=$(LENGTH) --format pylint

.PHONY: check-black
check-black:
	black --check --diff -v -l $(LENGTH) amocrm/v2 tests

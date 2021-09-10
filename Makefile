# Makefile for Python Wechaty
#
# 	GitHb: https://github.com/wechaty/python-wechaty
# 	Author: Huan LI <zixia@zixia.net> git.io/zixia
#

SOURCE_GLOB=$(wildcard bin/*.py src/wechaty_puppet_itchat/puppet.py tests/**/*.py)

#
# Huan(202003)
# 	F811: https://github.com/PyCQA/pyflakes/issues/320#issuecomment-469337000
#
IGNORE_PEP=E203,E221,E241,E272,E501,F811

# help scripts to find the right place of wechaty module
export PYTHONPATH=src/

.PHONY: all
all : clean lint

.PHONY: clean
clean:
	rm -fr dist/*

.PHONY: lint
lint: pylint pycodestyle flake8 mypy pytype

.PHONY: pylint
pylint:
	pylint \
		--load-plugins pylint_quotes \
		--disable E0401,W0511,C0302 \
		$(SOURCE_GLOB)

.PHONY: pycodestyle
pycodestyle:
	pycodestyle \
		--statistics \
		--count \
		--ignore="${IGNORE_PEP}" \
		$(SOURCE_GLOB)

.PHONY: flake8
flake8:
	flake8 \
		--ignore="${IGNORE_PEP}" \
		$(SOURCE_GLOB)

.PHONY: mypy
mypy:
	MYPYPATH=stubs/ mypy --install-types \
		$(SOURCE_GLOB)

.PHONE: pytype
pytype:
	pytype -V 3.7 \
		--disable=import-error,pyi-error \
		src/wechaty_puppet_itchat/puppet.py

.PHONY: uninstall-git-hook
uninstall-git-hook:
	pre-commit clean
	pre-commit gc
	pre-commit uninstall
	pre-commit uninstall --hook-type pre-push

.PHONY: install-git-hook
install-git-hook:
	# cleanup existing pre-commit configuration (if any)
	pre-commit clean
	pre-commit gc
	# setup pre-commit
	# Ensures pre-commit hooks point to latest versions
	pre-commit autoupdate
	pre-commit install
	pre-commit install --overwrite --hook-type pre-push

.PHONY: install
install:
	pip3 install -r requirements.txt
	pip3 install -r requirements-dev.txt
	# install pre-commit related hook scripts
	$(MAKE) install-git-hook

.PHONY: pytest
pytest:
	python3 -m pytest src/ tests/ -sv

.PHONY: test-unit
test-unit: pytest

.PHONY: test
test: lint pytest

code:
	code .

.PHONY: run
run:
	python3 bin/run.py

.PHONY: dist
dist:
	python3 setup.py sdist bdist_wheel

.PHONY: publish
publish:
	PATH=~/.local/bin:${PATH} twine upload dist/*

.PHONY: version
version:
	@newVersion=$$(awk -F. '{print $$1"."$$2"."$$3+1}' < VERSION) \
		&& echo $${newVersion} > VERSION \
		&& git add VERSION \
		&& git commit -m "🔥 update version to $${newVersion}" > /dev/null \
		&& git tag "v$${newVersion}" \
		&& echo "Bumped version to $${newVersion}"

.PHONY: deploy-version
deploy-version:
	echo "VERSION = '$$(cat VERSION)'" > src/wechaty_puppet_itchat/version.py

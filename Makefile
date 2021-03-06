DESTDEV = /media/jepler/CIRCUITPY
PYTHON = .venv/bin/python

default: install

.PHONY: install
install: cp
	@rsync --max-delete=0 --modify-window=2 -avO CIRCUITPY/ $(DESTDEV)/
	@sync

.PHONY: dist
dist: cp
	# This seems to be the easiest way to get the zip to have the desired top-level name
	cp -r CIRCUITPY JEplayer
	rm -f JEplayer.zip
	zip -9r JEplayer.zip JEplayer
	rm -rf JEplayer

.PHONY: clean
clean:
	rm -rf CIRCUITPY .venv build_deps

.PHONY: cp
cp:
	$(PYTHON) install.py

.PHONY: lint
lint:
	$(PYTHON) -mpylint src/*.py

.PHONY: venv
venv: .venv/bin/python

.venv/bin/python:
	python3 -mvenv --clear .venv
	$(PYTHON) -mpip install wheel
	$(PYTHON) -mpip install -r requirements.txt

DESTDEV = /media/jepler/CIRCUITPY
PYTHON = .venv/bin/python

default: install

.PHONY: install
install: cp
	rsync --max-delete=0 --modify-window=2 -av CIRCUITPY/ $(DESTDEV)/
	sync

.PHONY: dist
dist: cp
	# This seems to be the easiest way to get the zip to have the desired top-level name
	cp -r CIRCUITPY pyrockout
	rm -f pyrockout.zip
	zip -9r pyrockout.zip pyrockout
	rm -rf pyrockout

.PHONY: clean
clean:
	rm -rf CIRCUITPY .venv build_deps

.PHONY: cp
cp:
	$(PYTHON) install.py

.PHONY: venv
venv: .venv/bin/python

.venv/bin/python:
	/usr/bin/python3 -mvenv --clear .venv
	$(PYTHON) -mpip install wheel
	$(PYTHON) -mpip install -r requirements.txt

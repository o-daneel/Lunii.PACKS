VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYINST = $(VENV)/bin/pyinstaller

# RUNNING FROM PYTHON
run: $(VENV)/bin/activate
	$(PYTHON) src/lunii-packs.py

# BINARY
build: $(VENV)/bin/activate $(PYINST)
	$(PYINST) lunii-packs.spec

# VENV RELATED
$(VENV)/bin/activate: requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -r requirements.txt

$(PYINST):
	$(PYTHON) -m venv $(VENV)
	$(PIP) install pyinstaller

# CLEANING STUFF
mrproper: clean
	@rm -fr build
	@rm -fr dist

clean:
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete
	@rm -rf $(VENV)

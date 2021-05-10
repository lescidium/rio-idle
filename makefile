MODULENAME = value_investing 

help:
	@echo ""
	@echo "Welcome to my project!!!"
	@echo "To get started create an environment using:"
	@echo "	make init"
	@echo "	conda activate ./envs"
	@echo ""
	@echo "To generate project documentation use:"
	@echo "	make docs"
	@echo ""
	@echo "To Lint the project use:"
	@echo "	make lint"
	@echo ""
	@echo "To run unit tests use:"
	@echo "	make test"
	@echo ""


init:
	conda env create --prefix ./envs --file environment.yml

docs:
	cd $MODULENAME
	pdoc3 --force --html --output-dir ./docs scrape.py
	pdoc3 --force --html --output-dir ./docs calc.py
	pdoc3 --force --html --output-dir ./docs write.py
	cd ../

lint:
	cd $MODULENAME
	pylint scrape.py
	pylint calc.py
	pylint write.py
	cd ../

test:
	$env:PYTHONPATH = "C:\Users\Kenny\Documents\Spring_2021\value_investing\value_investing"
	cd $MODULENAME
	pytest -v


.PHONY: init docs lint test

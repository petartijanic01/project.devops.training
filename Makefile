.PHONY: deps

install-deps:
	python3 -m venv venv; source venv/bin/activate; pip install -r requirements.txt

test-units:
	source venv/bin/activate; python tests/units.py

docker-build:
	docker build -t tomfern/final-project:latest .



run:
	python -O python/main.py

run-debug:
	python python/main.py

requirements:
	sudo apt-get install libatlas-base-dev
	pip install -r requirements.txt

run:
	python -O club_controller/main.py

run-debug:
	python club_controller/main.py

requirements:
	sudo apt-get install libatlas-base-dev
	pip install -r requirements.txt

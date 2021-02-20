requirements:
	sudo apt-get install libatlas-base-dev
	pip install -r requirements.txt

run: export FLASK_DEBUG=1
run: export FLASK_APP=web-server/server.py
run:
	python -m flask run

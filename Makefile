#run: export FLASK_DEBUG=0
#run: export FLASK_APP=python/web_server/server.py
run:
	python -O python/web-web_server/server.py

#run-debug: export FLASK_ENV=development
#run-debug: export FLASK_APP=python/web_server/server.py
run-debug:
	python python/web_server/server.py

requirements:
	sudo apt-get install libatlas-base-dev
	pip install -r requirements.txt

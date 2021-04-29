SHELL := /bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
DOCKER_NAME=club_controller_server
SERVER_UDP_PORT=60123
WEB_SOCKET_PORT=60124

build:
	docker build -t $(DOCKER_NAME) .

build-nc: ## Build the container without caching
	docker build --no-cache -t $(DOCKER_NAME) .

run:
	docker run -it --device /dev/snd --rm -p=$(SERVER_UDP_PORT):$(SERVER_UDP_PORT)/udp -p=$(WEB_SOCKET_PORT):$(WEB_SOCKET_PORT) --name="$(DOCKER_NAME)" $(DOCKER_NAME)

up: build run

stop:
	docker stop $(DOCKER_NAME); docker rm $(DOCKER_NAME)

run-local:
	source ~/.virtualenvs/club-controller/bin/activate && \
	python3 -O $(ROOT_DIR)/club_controller/main.py

run-local-gui:
	source ~/.virtualenvs/club-controller/bin/activate && \
	python3 -O $(ROOT_DIR)/club_controller/main.py --gui

run-local-debug:
	python3 $(ROOT_DIR)/club_controller/main.py

run-local-debug-gui:
	source ~/.virtualenvs/club-controller/bin/activate && \
	python3 $(ROOT_DIR)/club_controller/main.py --gui

requirements: # TODO if not raspi pip3 install pyqt5==15.15.4
	pip3 install -r requirements.txt
	pip3 install -e .

dependencies:
	apt-get update && apt-get install -y \
		portaudio19-dev \
		python3-pyaudio\
		libasound-dev\
		libatlas-base-dev \
		psmisc


dependencies-gui-rpi:
	apt-get install python3-pyqt5

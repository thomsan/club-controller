UI_DOCKER_NAME=club_controller_ui
PORT=8080

run:
	python -O club_controller/main.py

run-debug:
	python club_controller/main.py

requirements:
	sudo apt-get install libatlas-base-dev
	pip install -r requirements.txt

ui-build:
	docker build -t $(UI_DOCKER_NAME) ui/club_controller_ui/

ui-build-nc: ## Build the container without caching
	docker build --no-cache -t $(UI_DOCKER_NAME) ui/club_controller_ui/

ui-run:
	docker run -it --rm -p=$(PORT):4040 --name="$(UI_DOCKER_NAME)" $(UI_DOCKER_NAME)

ui-up: ui-build ui-run

ui-stop:
	docker stop $(UI_DOCKER_NAME); docker rm $(UI_DOCKER_NAME)

flutter-watch:
	cd ui/club_controller_ui/ && flutter pub run build_runner watch

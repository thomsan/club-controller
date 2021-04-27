UI_DOCKER_NAME=club_controller_ui
UI_PORT=8080

build:
	docker build -t $(UI_DOCKER_NAME) club_controller_ui/

build-nc: ## Build the container without caching
	docker build --no-cache -t $(UI_DOCKER_NAME) club_controller_ui/

run:
	docker run -it --rm -p=$(UI_PORT):4040 --name="$(UI_DOCKER_NAME)" $(UI_DOCKER_NAME)

up: build run

stop:
	docker stop $(UI_DOCKER_NAME); docker rm $(UI_DOCKER_NAME)

flutter-watch:
	cd club_controller_ui/ && flutter pub run build_runner watch

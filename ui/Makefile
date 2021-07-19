UI_DOCKER_NAME=club_controller_ui
UI_PORT=60125

build:
	docker build -t $(UI_DOCKER_NAME) .

build-nc: ## Build the container without caching
	docker build --no-cache -t $(UI_DOCKER_NAME) .

run:
	docker run -it --rm -p=$(UI_PORT):$(UI_PORT) --name="$(UI_DOCKER_NAME)" $(UI_DOCKER_NAME)

up: build run

stop:
	docker stop $(UI_DOCKER_NAME); docker rm $(UI_DOCKER_NAME)

flutter-watch:
	cd club_controller_ui/ && flutter pub get && flutter pub run build_runner watch

dependencies:
	sudo snap install flutter --classic
	flutter channel master
	flutter upgrade
	flutter config --enable-web
	flutter doctor -v

build-local:
	cd club_controller_ui && \
	flutter pub get && \
	flutter pub run build_runner build --delete-conflicting-outputs && \
	flutter build web

run-local:
	echo 'Starting server on port' $(UI_PORT) '...'
	cd club_controller_ui/build/web && \
	python3 -m http.server $(UI_PORT)

build-android:
	# NOT YET IMPLEMENTED

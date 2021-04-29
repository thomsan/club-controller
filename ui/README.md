# Club Controller UI

This is the UI for the Club Controller.
The UI connects to the Club Controller Server via websocket.
The UI is build with flutter and can be build for Android, iOS, Web and Standalone (Windows, Mac, Linux Standalone not testet yet).

The UI can be build for web and served as a website, so every device in the network can connect via browser.

Therefore a simple web server is included in [web_server/](./web_server/).

# Building the UI
```
make dependecies
make build-local
```

# Running the UI web server localy
```
make run-local
```
Open the browser with the given address

# Deploy to android
```
make build-android
```
# Install dependencies
FROM debian:latest AS build-env
RUN apt-get update
RUN apt-get install -y curl git wget unzip libgconf-2-4 gdb libstdc++6 libglu1-mesa fonts-droid-fallback lib32stdc++6 python3 psmisc
RUN apt-get clean

# Document the exposed port
EXPOSE 60125

# Clone the flutter repo
RUN git clone https://github.com/flutter/flutter.git /usr/local/flutter

# Set flutter path
ENV PATH="/usr/local/flutter/bin:/usr/local/flutter/bin/cache/dart-sdk/bin:${PATH}"

# Enable flutter web
RUN flutter channel master
RUN flutter upgrade
RUN flutter config --enable-web

# Run flutter doctor
RUN flutter doctor -v

# Set the working directory to the app files within the container
WORKDIR /usr/local/bin/app/club_controller_ui

# Get App Dependencies
COPY club_controller_ui/pubspec.yaml /usr/local/bin/app/club_controller_ui/
COPY club_controller_ui/pubspec.lock /usr/local/bin/app/club_controller_ui/
RUN flutter pub get

# Build the app for the web
COPY . /usr/local/bin/app
RUN flutter build web

# Set the server startup script as executable
RUN ["chmod", "+x", "/usr/local/bin/app/web_server/server.sh"]

# Start the web server
ENTRYPOINT [ "/usr/local/bin/app/web_server/server.sh" ]

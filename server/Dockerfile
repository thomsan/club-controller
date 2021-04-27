# Install dependencies
FROM debian:latest AS build-env

# Set the working directory to the app files within the container
WORKDIR /usr/local/bin/app

# Copy the Makefile to the container
COPY Makefile .

# Install dependencies
RUN apt-get update && apt-get install -y make python3 python3-pip
RUN make dependencies
RUN apt-get autoremove && apt-get clean

# Install python packages
COPY requirements.txt .
RUN make requirements

# Copy all app files to the container
COPY . .
RUN pip3 install -e .

# Document the exposed port
EXPOSE 60123
EXPOSE 60124

# Set the server startup script as executable
RUN ["chmod", "+x", "/usr/local/bin/app/server.sh"]

# Start the server
ENTRYPOINT [ "/usr/local/bin/app/server.sh" ]

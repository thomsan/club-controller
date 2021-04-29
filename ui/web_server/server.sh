#!/bin/bash

# Welcome
echo 'Server start script initialized...'

# Set the port
PORT=60125

# Kill anything that is already running on that port
echo 'Cleaning port' $PORT '...'
fuser -k 60125/tcp

# Change directories to the release folder
cd club_controller_ui/build/web/

# Start the server
echo 'Starting server on port' $PORT '...'
python3 -m http.server $PORT

# Exit
echo 'Server exited...'

echo "Press any key to exit"
while [ true ] ; do
read -t 3 -n 1
if [ $? = 0 ] ; then
exit ;
fi
done

#!/bin/bash

# Welcome
echo 'Server start script initialized...'

# Set the port
PORT=60125

# Kill anything that is already running on that port
echo 'Cleaning port' $PORT '...'
fuser -k 60125/tcp

# Start the server
make run-local

# Exit
echo 'Server exited...'

echo "Press any key to exit"
while [ true ] ; do
read -t 3 -n 1
if [ $? = 0 ] ; then
exit ;
fi
done

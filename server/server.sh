#!/bin/bash

# Welcome
echo 'Club Controller server start script initialized...'

# Set the ports
SERVER_UDP_PORT=60123
WEB_SOCKET_PORT=60124

# Kill anything that is already running on that port
echo 'Cleaning SERVER_UDP_PORT' $SERVER_UDP_PORT '...'
fuser -k $SERVER_UDP_PORT/udp

# Kill anything that is already running on that port
echo 'Cleaning WEB_SOCKET_PORT' $WEB_SOCKET_PORT '...'
fuser -k $WEB_SOCKET_PORT/tcp

# Start the server
echo 'Starting Club Controller server  ...'
if [[ " $@ " =~ " --gui " ]]; then
    make run-local-gui
else
    make run-local
fi

# Exit
echo 'Club Controller server exited...'

echo "Press any key to exit"
while [ true ] ; do
read -t 3 -n 1
if [ $? = 0 ] ; then
exit ;
fi
done

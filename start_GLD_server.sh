#!/bin/bash


# Start the GLD server and backend script:

echo "Killing previous screen sessions..."
screen -S GLD_webserver -X quit
screen -S GLD_backend -X quit

echo "Starting web server"
screen -S GLD_webserver -d -m python -m SimpleHTTPServer 8000

echo "Starting GLD backend"
screen -S GLD_backend -d -m ipython GLD_server_websocket.py


echo "Don't forget to mount the source directory!"

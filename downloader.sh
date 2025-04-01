#!/bin/bash

command -v python3 >/dev/null 2>&1 || { echo "Python3 is not installed. Please install Python3." >&2; exit 1;}
command -v pip3 >/dev/null 2>&1 || { echo "pip3 is not installed. Please install pip3." >&2; exit 1;}

if [ -f "requirements.txt" ]; then
	echo "Installing dependencies from requirements.txt..."
	pip3 install -r requirements.txt
else
	echo "requirements.txt not found. Please ensure the file exists."
	exit 1
fi

echo "Please enter your API key:"
read -s API_KEY

export API_KEY="$API_KEY"


echo "All dependencies installed and API key configured successfully"

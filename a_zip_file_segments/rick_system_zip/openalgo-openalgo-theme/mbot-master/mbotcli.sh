#!/bin/bash

# Navigate to the directory containing the script, regardless of where the script is invoked from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment if it exists
if [ -f "$DIR/mbot-env12/bin/activate" ]; then
	source "$DIR/mbot-env12/bin/activate"
else
	echo "Could not find the virtual environment."
	echo "Please run the setup script to create the virtual environment"
	echo "and install the required packages."
	echo "Exiting..."
	exit 1
fi

# Run the CLI
python3 "$DIR/src/mbotcli.py" "$@"

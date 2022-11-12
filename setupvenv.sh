#!/bin/sh

if [[ $OSTYPE == *"darwin"* ]]; then
	if [[ $ZSH_EVAL_CONTEXT == 'toplevel' ]]; then
		echo "ERROR: Script is expected to be run using source ./setupvenv.sh"
		echo "Exiting without executing."
		exit
	fi
else
	if [[ $_ == $0 ]]; then # on Windows WSL Ubunto
		echo "ERROR: Script is expected to be run using source ./setupvenv.sh"
		echo "Exiting without executing."
		exit 1
	fi
    # TODO: How to test in windows power shell
fi

echo "Running Enviroment Setup"
echo "1. Checking if Python Virtual Environment already exists:"
VENV_DIR="./venv"
if [ ! -d "$VENV_DIR" ]; then  
	echo "1a. Creating Python virtual enviroment into ./vene"
	if [[ $OSTYPE == "linux-gnu" ]]; then  # Windows WSL Ubuntu??
		python3 -m venv ./venv
	elif [[ $OSTYPE == *"darwin"* ]]; then
		python3 -m venv ./venv
	else  # Windows OS???
        python3 -m venv ./venv
    fi
	VENV_REQUIRE_SETUP=1
else
	echo "$VENV_DIR exist. Skip Step 1."
fi

echo "2. Activating Python virtual enviroment"
source venv/bin/activate

if [[ "$VENV_REQUIRE_SETUP" -eq 1 ]]; then
	echo "3a. Installing required python packages"
	pip install --upgrade pip
	pip install -r requirements.txt

	echo "3b. Installing Steer Behaviour into the python virtual enviroment"
	pip install -e .
else
	echo "$VENV_DIR exist. Skipping step 3 - package install"
fi

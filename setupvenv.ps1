$isDotSourced = $MyInvocation.InvocationName -eq '.' -or $MyInvocation.Line -eq ''
if (!$isDotSourced) {
    Write-Output "ERROR: Script is expected to be run using . .\setupvenv.ps1"
    Write-Output "Exiting without executing."
    exit
}

Write-Output "Running Enviroment Setup"
Write-Output "1. Checking if Python Virtual Environment already exists:"
$VENV_DIR=".\venv"
$VENV_REQUIRE_SETUP=0
if (!(Test-Path $VENV_DIR)) {
    Write-Output "1a. Creating Python virtual enviroment into ./venv"
    python3 -m venv .\venv
    $VENV_REQUIRE_SETUP=1
} else {
    Write-Output "$VENV_DIR exist. Skip Step 1."
}

Write-Output "2. Activating Python virtual enviroment"
. .\venv\Scripts\activate.ps1

if ($VENV_REQUIRE_SETUP -eq 1) {
    Write-Output "3. Install packages"
    Write-Output "3a. Installing required python packages"
    python -m pip install --upgrade pip
    pip install -r requirements.txt

    Write-Output "3b. Installing Steer Behaviour into the python virtual enviroment"
    pip install -e .

    Write-Output "3c. Install pre-commit hooks"
    pre-commit install
} else {
    Write-Output "$VENV_DIR exist. Skipping step 3 - package install"
}

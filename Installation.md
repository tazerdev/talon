# Talon Installation

Before you can get started with Talon, you will need to clone this repository and create a Python virtual environment for it.

## Prerequisites

You will need both Git and Python in order to clone the Talon repository and then work with the various Talon utilities. These are both freely available and, if you're already working with NFC engines like Nighthawk, you may already have them installed. Technically, you don't need Git as you can download a copy of the project in Zip format from the Releases tab.

Under Linux you will need gcc-c++, gcc-fortran, openblas, openblas-devel, lapack-devel, and flang. This is for pip when it installs and builds the various dependencies.

## Cloning the Repository

First, on the CLI, navigate to the location you prefer for the Talon repository to live. In this example I clone a copy of the repository in my development directory.

Windows:

```shell
cd C:/Users/username
git clone https://github.com/tazerdev/talon.git
```

Linux:

```shell
cd /home/username
git clone https://github.com/tazerdev/talon.git
```

## Creating a Python Virtual Environment

The next step is to create a Python venv for the project. I like to keep my venvs together so I don't have them scattered about. In this example I create a Talon virtual environment under the venvs folder.

 Windows & Linux
: 
```shell
mkdir /home/username/venvs
cd /home/username/venvs
python -m venv talon-venv
```

And then activate it:

Windows:

```shell
& C:/Users/username/venvs/talon-venv/Scripts/Activate.ps1
```

Linux:

```shell
source /home/username/venvs/talon-venv/bin/activate
```

## Install Python Requirements

Talon requires a number of additional Python modules in order to work. These dependencies are captured in a requirements.txt file in the Talon repository folder. We simply need to feed that file to pip and wait for a few minutes for the install to complete:

Windows:

```shell
cd C:/Users/username/talon
pip install -r ./requirements.txt
```

Linux:

```shell
cd /home/username/talon
pip install -r ephem guano requests astral sounddevice soundfile wxpython librosa matplotlib
```

## Setup Windows Command Aliases

The typical way to execute a Python script, under Windows, is to provide the full path to the Python binary, the full path to the script that you wish to execute, and any additional command line arguments. Since all of the Talon utilities require a configuration file be supplied as an argument, this means an additional full path to the config file. You end up with a command that looks like this:

```shell
C:/Users/username/devel/venvs/talon-venv/Scripts/python.exe C:/Users/username/devel/talon/bin/talon-gui -c C:/Users/username/devel/talon/etc/talon.ini
```

If you're using PowerShell, which is recommended, then you can run a script to turn each command into a short alias:

```shell
. C:/Users/username/talon/bin/Add-TalonAliases.ps1
```

The alias equivalent to the command above is simply:

```shell
talon-gui
```

## Post-Installation

Once the installation is complete, you just need to run the following commands in a new PowerShell window:

Windows:

```shell
& C:/Users/username/venvs/talon-venv/Scripts/Activate.ps1
. C:/Users/username/talon/bin/Add-TalonAliases.ps1
```

Linux:

```shell
source /home/username/venvs/talon-venv/bin/activate
source /home/username/talon/bin/Add-TalonAliases.sh
```

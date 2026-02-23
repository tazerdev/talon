# Installation Demo

Make a directory to contain the python virtual environment and talon repository, then cd into it:

```shell
mkdir demo
cd demo
```

Clone the talon repository, or grab a copy of the latest release archive and extract it in the demo directory:

```shell
git clone https://www.github.com/tazerdev/talon.git
```

Create the Python virtual environment:

```shell
python -m venv talon-venv
```

Activate the talon virtual environment:

```shell
& .\talon-venv\Scripts\activate.ps1
```

Install the Python dependencies, which will take several minutes (2.67 minutes). Note, under Linux you'll need to install several development libraries before this step, as Python has to complie some modules from scratch.:

```shell
pip install ephem guano requests astral sounddevice soundfile wxpython librosa matplotlib
```

Load talon alises:

```shell
. talon/bin/Add-TalonAliases.ps1
```

So you can run this:

```shell
talon
```

instead of this:

```shell
c:/users/mark/demo/talon-venv/Scripts/python.exe c:/users/mark/demo/talon/bin/tlist -c c:/user/mark/demo/talon/talon.ini 
```

Create a talon.ini file:

```ini
[general]
default = RPI1
audacity_path = C:/Program Files/Audacity/audacity.exe

[taxonomy]
ebird_taxonomy = taxonomy/eBird_taxonomy_v2025.csv
group_code_xref = taxonomy/group_code_xref.csv

[RPI1]
type = station
latitude = 35.780480199773415
longitude = -78.63909694937483
timezone = US/Eastern
file_format = RPI1_%Y%m%d_%H%M%S%z.WAV

[RPI1.audio]
device=Microphone (HD Audio Microphone 2)
rate=48000
channels=1
bits=24
```

File format fields:

```
_  - Field separator

%Y - year
%m - month
%d - day
%H - hour (24-hour format)
%M - minute
%S - second
%z - UTC offset
```

Change to a directory with WAV files and go through the various utilities.

## tlist

Run tlist, show the tabular format, describe the fields, and then show the JSON output.

## tmdupdate

Run tmdupdate, show the metadata. Explain that after filling out the RPI1.metadata section, that data will be used to populate the GUANO header.

Optional metadata:

```ini
[RPI1.metadata]
name = North Carolina State Capitol Building
note = DIY microphone (48V phantom power), connected to a Roland Rubix 22, permanently located on the back deck.
location = Raleigh, NC
elevation = 466ft
make = Raspberry Pi Foundation
model = Raspberry Pi 5 Model B Rev 1.0
serial = f003d4d5d87e439e
copyright = Mark Montazer
```

## tsplit

Run tsplit, showing --metadata output. Then split a file as an example.

## tweather

Run tweather, describing its features.

## trecord

Run trecord --schedule to show the scheduler. Run trecord in debug mode to show it doing a recording.
Discuss creating a trecord scheduled task (which runs on login, or on boot which requires a password)

## talon

Run talon, go over filter.csv, filter output by species, engine, protocol, etc. Extract audio clips demonstrating how fast it is. Extract some clips explaining how slow it is in general (30 minutes for the demo dir) but how fast it can be with multiprocessing (4.67 minutes for the demo dir).

Remove the clips dir and then move the clips dir from ./bak to ./

## talon-gui

Talk about cleaning up excluded files to save space, maybe even deleting the original WAV files and just keeping the clips (currently exploring this option, but might need to wait until I add supplemental file support so users can add detections by way of an audacity labels file)

Demo confirm, exclude, override, restore, duplicate
Demo filtering (day, nocturnal, nfc, species drop down, date/time, engine, etc)
Demo time series graph
Demo pseudo checklists
Demo tweather

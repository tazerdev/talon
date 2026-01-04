# Talon

## Overview

Talon is a set of utilities for working with BirdNET and Nighthawk detections files. It will classify detections based on eBird protocol (NFC or Daytime), extract audio clips and generate spectrographs for all detections the user specifies, as well as generate eBird checklists. It can also be used to capture audio, split audio files, manage GUANO compatible WAV metadata, and get weather observations and forecasts for a given location.

## Installation

Please read the [installation document](INSTALL.md) for more details on how to clone the repository, setup a python virtual environment, and setup convenience aliases for the various commands. The primary difference between Windows and Linux configurations will be paths. In Windows your home folder is likely under C:/Users and in Linux it's under /home. Just be sure to update the path in all instructions accordingly.

## Configuration

At the heart of Talon is a set of metadata required to calculate the absolute date and time of each detection, and the date and times of the Nocturnal Flight Call window (astronomical dusk to astronomical dawn.) This requires, at a minimum, a set of GPS coordinate and a time zone (from which a UTC offset can be determined.) This data is placed in an INI file located in the talon/etc/talon.ini.

## File Naming Convention

Talon will not recognize any file which it hasn't been informed of via the INI file below. The scheme I use, which I know works, is UID_YYYYMMDD_HHMMSS-ZZZZ.WAV. If you're familiar with how Python parses datetimes from strings, then you have some leeway in how your files are named. The.

## talon.ini

### General

The general section is used to inform the various talon utilities. A general section under Windows will look like this:

```ini
[general]
default = RPI1
cachedir = C:/users/username/talon/var/cache

# To hide detections for a given species which are under the
# supplied threshold, add them to filter.csv in a CSV format:
# Eastern Screech-Owl,.5
species_filter = C:/users/username/talon/var/filter.csv

# Path to the Audacity binary on your local system
audacity_path = C:/Program Files/Audacity/audacity.exe

# Icons used by the app itself:
# https://github.com/tabler/tabler-icons
icon_path = C:/users/username/talon/var/icons
```

And general section under Linux will look like this:

```ini
[general]
default = RPI1
cachedir = /home/username/talon/var/cache

# To hide detections for a given species which are under the
# supplied threshold, add them to filter.csv in a CSV format:
# Eastern Screech-Owl,.5
species_filter = /home/username/talon/var/filter.csv

# Path to the Audacity binary on your local system
audacity_path = /usr/sbin/audacity

# Icons used by the app itself:
# https://github.com/tabler/tabler-icons
icon_path = /home/username/talon/var/icons
```

### Taxonomy

This is used to convert BirdNet and Nighthawk detections to common names. It's also the source behind the search box which allows you to override a detection. The group code cross-reference is a list of Nighthawk group codes and their nearest corresponding eBird taxonomy (e.g., 'spuh'):

Windows:

```ini
[taxonomy]
# eBird Taxonomy can be acquired from https://...
ebird_taxonomy = C:/users/username/talon/var/taxonomy/eBird_taxonomy_v2025.csv

# Groupcodes utized by Nighthawk, but cross-referenced to the neares eBird 'spuh'
group_code_xref = C:/users/username/talon/var/taxonomy/group_code_xref.csv
```

Linux:

```ini
[taxonomy]
# eBird Taxonomy can be acquired from https://...
ebird_taxonomy = /home/username/talon/var/taxonomy/eBird_taxonomy_v2025.csv

# Groupcodes utized by Nighthawk, but cross-referenced to the neares eBird 'spuh'
group_code_xref = /home/username/talon/var/taxonomy/group_code_xref.csv
```

### Location

Location is used to inform the Talon utils which WAV files it can work with. Specifically

```ini
[RPI1]
type = station
name = North Carolina State Capitol Building
note = DIY microphone (48V phantom power), connected to a Roland Rubix 22, permanently located on the back deck.
location = Raleigh, NC
elevation = 466ft
latitude = 35.780480199773415
longitude = -78.63909694937483
timezone = US/Eastern
make = Raspberry Pi Foundation
model = Raspberry Pi 5 Model B Rev 1.0
serial = f003d4d5d87e439e
copyright = Mark Montazer
file_format = RPI1_%%Y%%m%%d_%%H%%M%%S%%z.WAV
weather_station = KRDU
ebird_region = US-NC-037

[RPI1.audio]
; run trecord --list to get the device name
device=Microphone (HD Audio Microphone 2)
rate=48000
channels=1
bits=24
```

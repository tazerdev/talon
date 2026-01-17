# Talon

## Overview

Talon is a set of utilities for working with BirdNET and Nighthawk detections files. It will classify detections based on eBird protocol (NFC or Daytime), extract audio clips and generate spectrographs for all detections the user specifies, as well as generate eBird checklists. It can also be used to capture audio, split audio files, manage GUANO compatible WAV metadata, and get weather observations and forecasts for a given location.

## Installation

Please read the [installation document](INSTALL.md) for more details on how to clone the repository, setup a python virtual environment, and setup convenience aliases for the various commands. The primary difference between Windows and Linux configurations will be paths. In Windows your home folder is likely under C:/Users and in Linux it's under /home. Just be sure to update the path in all instructions accordingly.

## Configuration

At the heart of Talon is a set of metadata required to calculate the absolute date and time of each detection, and the date and times of the Nocturnal Flight Call window (astronomical dusk to astronomical dawn.) This requires, at a minimum, a set of GPS coordinate and a time zone (from which a UTC offset can be determined.) This data is placed in an INI file located in the talon/talon.ini.

## talon.ini

### General

The general section is used to inform the various talon utilities of details for various location. Several utilities will fall back to the default option when the location isn't specified on the command line. The utilities which work with WAV files will always attempt to use the UID in the file name to pull relevant data.

A general section under Windows will look like this:

```ini
[general]
default = RPI1

# Path to the Audacity binary on your local system
audacity_path = C:/Program Files/Audacity/audacity.exe
```

And general section under Linux will look like this:

```ini
[general]
default = RPI1

# Path to the Audacity binary on your local system
audacity_path = /usr/sbin/audacity
```

### Taxonomy

This is used to convert BirdNet and Nighthawk detections to common names. It's also the source behind the search box which allows you to override a detection. The group code cross-reference is a list of Nighthawk group codes and their nearest corresponding eBird taxonomy (e.g., 'spuh'). The paths to these files are relative to the talon directory. It's best to leave these options alone.

Linux and Windows example:

```ini
[taxonomy]
# eBird Taxonomy can be acquired from https://...
ebird_taxonomy = taxonomy/eBird_taxonomy_v2025.csv

# Groupcodes utized by Nighthawk, but cross-referenced to the neares eBird 'spuh'
group_code_xref = taxonomy/group_code_xref.csv
```

### File Naming Convention

Talon will not recognize any file which it hasn't been informed of via the INI file below. The standard file naming scheme (used by Talon and Wildlife Acoustics) uses underscores to seperate fiels:

```code
UID_YYYYMMDD_HHMMSS.WAV
```

Where UID is a variable length unique identifier, YYYYMMDD is date with the year (4-digit), month (2-digit, zero-padded), and day (2-digit, zero-padded), and HHMMSS is the 24-hour time. This naming scheme is customized in the location section described below, but can be any recognizable Python datetime scheme. You can read more about the format codes on the [Python datetime format codes page](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).

This example uses a serial number of a device as the UID:

```
56371E6A_20260104_122903.WAV
```

This example is the hostname of my local Raspberry Pi 5, note that it includes the UTC offset:

```
RPI1_20240906_050000-0400.WAV
```

Ultimately, Talon can determine the UTC offset by the time zone listed in the INI file, but including it in the file name isn't a bad idea in the event that you share the file with someone else.

### Location

This section contains the essential data necessary to calculate the exact start and end of the NFC window. Without this data talon can't proceed. Latitude, longitude, and time zone are necessary to calculate how far below the horizon the sun is at a given time for that location.

File format is used to associate the above location data to all files matching the format pattern. The standard format pattern contains three fields separated by underscores: a unique ID, the start date of the recording, and the start time of the recording. This format was settled on because it's used by at least one major audio recording vendor (i.e., Wildlife Acoustics.)

Latitude and longitude should be in decimal format. Time zone should be an entry from the time zone database, see the [Wikipedia Time Zone Database page](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for details.

The optional weather station field is used to set a default weather station for this location. You can get a list of locations by running 'tweather --list'.

```ini
[RPI1]
type = station
latitude = 35.780480199773415
longitude = -78.63909694937483
timezone = US/Eastern
file_format = RPI1_%%Y%%m%%d_%%H%%M%%S%%z.WAV
weather_station = KRDU
```

The metadata section is used to associate optional metadata with the location information above. The section title should always be in the form of UID.metadata. All fields are free form strings and can be written to WAV files using the tmdupdate utility.

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

### Audio

This section uses UID.audio to define audio parameters for recording. You can get a list of available recording devices by running the 'trecord --list' command. When trecord is run without command line parameters it will default to these settings.

```ini
[RPI1.audio]
; run trecord --list to get the device name
device=Microphone (HD Audio Microphone 2)
rate=48000
channels=1
bits=24
```

### Example

The following is a complete configuration file, though it contains no optional metadata nor an optional recording device:

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
file_format = RPI1_%%Y%%m%%d_%%H%%M%%S%%z.WAV
```

## Commands

More detail on the individual commands can be found in the [COMMANDS.md](COMMANDS.md) file.

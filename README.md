# Talon

## Overview

Talon is a set of utilities for working with BirdNET and Nighthawk detections files. It will classify detections based on eBird protocol (NFC or Daytime), extract audio clips and generate spectrographs for all detections the user specifies, as well as generate eBird checklists. It can also be used to capture audio, split audio files, manage GUANO compatible WAV metadata, and get weather observations and forecasts for a given location.

## Installation

Please read the [installation document](INSTALL.md) for more details on how to clone the repository, setup a python virtual environment, and setup convenience aliases for the various commands. The primary difference between Windows and Linux configurations will be paths. In Windows your home folder is likely under C:/Users and in Linux it's under /home. Just be sure to update the path in all instructions accordingly.

## Configuration

At the heart of Talon is a set of metadata required to calculate the absolute date and time of each detection, and the date and times of the Nocturnal Flight Call window (astronomical dusk to astronomical dawn.) This requires, at a minimum, a set of GPS coordinate and a time zone (from which a UTC offset can be determined.) This data is placed in an INI file located in the talon/etc/talon.ini.

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

### File Naming Convention

Talon will not recognize any file which it hasn't been informed of via the INI file below. The standard file naming scheme (used by Talon and Wildlife Acoustics) uses underscores to seperate fiels:

```code
UID_YYYYMMDD_HHMMSS.WAV
```

Where UID is a variable length unique identifier, YYYYMMDD is date with the year (4-digit), month (2-digit, zero-padded), and day (2-digit, zero-padded), and HHMMSS is the 24-hour time. This naming scheme is customized in the location section described below, but can be any recognizable Python datetime scheme.

This example uses a serial number of a device as the UID:

    56371E6A_20260104_122903.WAV

This example is the hostname of my local Raspberry Pi 5, note that it includes the UTC offset:

    RPI1_20240906_050000-0400.WAV

Ultimately, Talon can determine the UTC offset by the time zone listed in the INI file, but including it in the file name isn't a bad idea in the event that you share the file with someone else.

### Location

This section will describe the metadata you wish to associate with files that match the supplied naming scheme. In this example any file that matches 'RPI1_%%Y%%m%%d_%%H%%M%%S%%z.WAV' will have the accompanying metadata associated with it. Without this metadata, Talon doesn't have the latitude and longitude of the recording station and subsequently can't calculate astronomical dawn/dusk to classify detections as the eBird NFC protocol, daytime or nocturnal.

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
```

Here's a description of the fields:

* \[UID\] - the text within the brackets is the UID described above.
* Type - this must be 'station' (lowercase) in order for Talon to know that this is metadata for a location.
* Name - a useful description of the name associated with related recordings, commonly the eBird hotspot you use when submitting NFC checklists.
* Note - a note to describe a bit more about the hardware used for recordings at this location.
* Location - the city and state/province of this location.
* Elevation - the elevation in feet of this location.
* Latitude - the latitude, in decimal, of this location.
* Longitude - the longitude, in decimal, of this location.
* Timezone - the time zone, as listed in the timezone database of this location. See [Wikipedia entry for Time Zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for a list.
* Make / Model / Serial - the make, model, and serial numbmer (if any) of the hardware used to record audio at this locaiton.
* Copyright - the copyright name you wish associated with recordings from this location.
* File Format - as described above, the Python datetime format string used to describe audio files for this location.
* Weather Station - the 4 digit weather.gov station ID for your location weather station. Once you have an INI file created you can use 'tweather --list' to get a list of stations and their distances.

### Location.Audio

This section uses UID.audio to define audio parameters for recording.

```ini
[RPI1.audio]
; run trecord --list to get the device name
device=Microphone (HD Audio Microphone 2)
rate=48000
channels=1
bits=24
```

Here's a description of the fields:

* Device - this is the recording device that will be used by 'trecord', you can get a list of devices by running 'trecord --list'.
* Rate - a bit rate supported by the recording device.
* Channels - the number of channels to record, typically 1.
* Bits - a bit depth supported by the recording device.

## Commands

More detail on the individual commands can be found in the [COMMANDS.md](COMMANDS.md) file.


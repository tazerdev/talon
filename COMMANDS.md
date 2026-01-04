# A Brief Introduction to the Talon Utilities

## tlist

This will generate a list of all recognized WAV files and give useful information about each including duration (in seconds and minutes), channels of audio, bit depth, rate, start time, stop time and whether or not the recording contains any NFC data. The last field, NFC data, is 0 for no NFC data and 1 otherwise. It can be useful for scripting, like if you want to run Nighthawk only on files with NFC data.

You can use the -j,--json parameter to dump metadata about all files, including all Nighthawk/BirdNet detections.

Example output:

```shell
> tlist
RPI1_20260103_120000-0500.WAV  659.06  59.99  1  32  48000  2026-01-03 12:00:00-0500  2026-01-03 12:59:59-0500  0
RPI1_20260103_130000-0500.WAV  659.05  59.99  1  32  48000  2026-01-03 13:00:00-0500  2026-01-03 13:59:59-0500  0
RPI1_20260103_140000-0500.WAV  659.05  59.99  1  32  48000  2026-01-03 14:00:00-0500  2026-01-03 14:59:59-0500  0
RPI1_20260103_150000-0500.WAV  659.05  59.99  1  32  48000  2026-01-03 15:00:00-0500  2026-01-03 15:59:59-0500  0
RPI1_20260103_160000-0500.WAV  659.05  59.99  1  32  48000  2026-01-03 16:00:00-0500  2026-01-03 16:59:59-0500  0
RPI1_20260103_170000-0500.WAV  659.05  59.99  1  32  48000  2026-01-03 17:00:00-0500  2026-01-03 17:59:59-0500  0
RPI1_20260103_180000-0500.WAV  659.05  59.99  1  32  48000  2026-01-03 18:00:00-0500  2026-01-03 18:59:59-0500  1
RPI1_20260103_190000-0500.WAV  659.05  59.99  1  32  48000  2026-01-03 19:00:00-0500  2026-01-03 19:59:59-0500  1
RPI1_20260103_200000-0500.WAV  659.05  59.99  1  32  48000  2026-01-03 20:00:00-0500  2026-01-03 20:59:59-0500  1
RPI1_20260103_210000-0500.WAV  659.05  59.99  1  32  48000  2026-01-03 21:00:00-0500  2026-01-03 21:59:59-0500  1
RPI1_20260103_220000-0500.WAV  659.05  59.99  1  32  48000  2026-01-03 22:00:00-0500  2026-01-03 22:59:59-0500  1
RPI1_20260103_230000-0500.WAV  659.05  59.99  1  32  48000  2026-01-03 23:00:00-0500  2026-01-03 23:59:59-0500  1
RPI1_20260104_000000-0500.WAV  659.05  59.99  1  32  48000  2026-01-04 00:00:00-0500  2026-01-04 00:59:59-0500  1
````

## talon

talon can be used to display all detection information, including curations generated in talon-gui, for all files in the specified directory (defaults to the current directory).

* -j, --json - Output the detection list in JSON format, suitable for consumption by another program
* -r, --recurse - Recurse and process all sub-directories.
* -s, --species - Display detections matching the supplied species name(s)
* -e, --engine - Display only detections from the supplied engine (e.g., bn = BirdNet, nh = Nighthawk, ta = Talon)
* -o, --protocol - Display only detections matching the supplied protocol (e.g., day = Diurnal, noc = Nocturnal, nfc = Nocturnal Flight Call)
* -t, --threshold - Display detections above this threshold.
* --station - If you have recordings from multiple stations in one directory (not recommended) you can use this to view a specific station's detections.
* --start - Display only detections occurring after this time.
* --duration - Display the duration, in hours, of detections froms the supplied start time.
* --clip - Extract audio clips, saved in the 'clips' directory of the path where the audio file resides, of all displayed detections.
* --graph - Generate spectrograms, saved in the 'clips' directory of the path where the audio file resides, of all displayed detections. Implies --clip.
* --force - Overwrite existing audio clips and spectrograms.
* --ful-heigh - Instead of graphing only the first 12kHz of the spectrum (the section most relevant for NFCs), graph the entire spectrum.
* --timeseries - Generate a time series graph of all displayed detections (saved as timeseries.png in the current working directory).
* --checklist - Group all detections into checklist-like tables. Suitable for aiding in the input of eBird checklists.
* --disposition - Display only the detections matching the specified disposition(s).

Fiels are the absolute date/time of the detection, the start time (relative to the WAV file), the location ID, the eBird protocol, the engine used to make the detection, the confidence/probability, and the Common Name (species code).

Example:

```shell
> talon
2025-12-15T20:11:18.000-05:00  00:11:18.00  RPI1  nfc  bn   58.15%  Eastern Screech-Owl (easowl1)
2025-12-15T20:11:21.000-05:00  00:11:21.00  RPI1  nfc  bn   76.79%  Eastern Screech-Owl (easowl1)
2025-12-15T20:35:03.000-05:00  00:35:03.00  RPI1  nfc  bn   75.00%  Black-crowned Night-Heron (bcnher)
2025-12-15T20:56:33.000-05:00  00:56:33.00  RPI1  nfc  bn   45.77%  Palm Warbler (palwar)
```

## tmdupdate

Used to display, or write (if using --force), metadata of each WAV file:

```shell
> tmdupdate RPI1_20251130_134420-0500.WAV
No existing GUANO header detected.

New GUANO header
------------------------------------------------------------
GUANO|Version: 1.0
Loc Elevation: 466ft
Loc Position: (35.780480199773415, -78.63909694937483)
Make: Raspberry Pi Foundation
Model: Raspberry Pi 5 Model B Rev 1.0
Serial: f003d4d5d87e439e
Original Filename: RPI1_20251130_134420-0500.WAV
Note: DIY microphone (48V phantom power), connected to a Roland Rubix 22, permanently located on the back deck.
Timestamp: 2025-11-30 13:44:20-05:00
NFC|Moon Phase: 0.7636281685282454
NFC|Station Name: North Carolina State Capitol Building
NFC|Time Zone: US/Eastern
NFC|Copyright: Mark Montazer
NFC|Location: Raleigh, NC
```

## tsplit

Used to extract a single audio channel (default 0) from a WAV file. 0 for the first channel (typically left), 1 for the second channel (typically right), etc. No metadata is copied with this command, just a bare WAV file with one channel of audio from the original. You can use tmdupdate to write metadata. Extracted channels are saved under the original filename with '-0' for channel 0, '-1' for channel 1, etc. You'll want to rename the files accordingly once you're confident you have the right channel.

```shell
> tsplit -i .\RPI1_20251130_134420-0500.WAV
Splitting channel 0 from .\RPI1_20251130_134420-0500.WAV: 100.00%
```

## tweather

Get a list of recent observations, or future forecast, from the weather station listed in the INI file for a given location.

* --list - Display a list of weather stations and distances closes to the GPS coordiantes of the locations
* --location - Defaults to whatever the default is in the INI file, otherwise will use the supplied location.
* --now - Display a one-line summary of conditions using the closest obervation date to now. Otherwise display a table of results.
* --samples - Display only the supplied number of observations and forecast hours.
* --si - Whether or not to use standard units or the US customary units (default)

Example 1, get the 5 most recent observations and the next 5 hours of forecast for the default station in the INI file:

```shell
> tweather -s 5
Future Forecast
---------------------------------------------------------------------------------
2026-01-04 19:00:00   42.00F   67.00%   2.00 mph E    32.00F  0.00%  Mostly Clear
2026-01-04 18:00:00   45.00F   60.00%   2.00 mph E    32.00F  0.00%  Clear
2026-01-04 17:00:00   50.00F   48.00%   1.00 mph E    31.00F  0.00%  Sunny
2026-01-04 16:00:00   53.00F   43.00%   1.00 mph NW   31.00F  0.00%  Sunny
2026-01-04 15:00:00   52.00F   44.00%   2.00 mph NW   31.00F  0.00%  Sunny
2026-01-04 14:00:00   51.00F   48.00%   3.00 mph NW   32.00F  0.00%  Sunny

Recent Observations
---------------------------------------------------------------------------------------------
2026-01-04 12:51:00   50.00F   49.83%   4.70 mph ---  ------  1019.30 mbar  10.00 mi  Clear
2026-01-04 11:51:00   46.04F   55.34%   4.70 mph S    43.77F  1020.00 mbar  10.00 mi  Clear
2026-01-04 10:51:00   44.06F   62.32%   4.70 mph SSE  41.46F  1020.70 mbar  10.00 mi  Clear
2026-01-04 09:51:00   37.94F   67.23%   0.00 mph N    ------  1020.00 mbar  10.00 mi
2026-01-04 08:51:00   33.08F   88.38%   0.00 mph N    ------  1019.30 mbar  10.00 mi  Clear
2026-01-04 07:51:00   28.04F   95.66%   0.00 mph N    ------  1018.30 mbar   9.00 mi  Clear
```

Example 2, get a one-liner of current conditions in US units and SI:

```shell
> tweather --now
Station ID: KRDU, Date: 2026-01-04, Time: 12:51:00, Temperature: 50.00F, Wind Chill: ------, Humidity: 49.83%, Wind Speed: 4.70 mph ---, Pressure: 1019.30 mbar, Visibility: 10.00 mi, Conditions: Clear, Cloud Layers:

> tweather --now --si
Station ID: KRDU, Date: 2026-01-04, Time: 12:51:00, Temperature: 10.00C, Wind Chill: ------, Humidity: 49.83%, Wind Speed: 7.56 km/h ---, Pressure: 101930 Pa, Visibility: 16.09 km, Conditions: Clear, Cloud Layers:
```

## trecord

trecord is used to record audio from the specified device. It attempts to align recording times based on duration (e.g., 1 hour recordings will start a the top of every hour, 10-minute recordings at 00, 10, 20, 30, etc). The exception to this are the first recording, where it'll record a short duration until it can begin aligned recordings, and at the NFC start/stop windows. By starting/stopping recordings at the NFC threshold, this ensures the necessary data is saved if, say, you only want NFC recordings.

Note that trecord will record continuously until terminated with CTRL-C. Upon completion of each recording, or termination, it will write metadata from the INI file to each recording.

* --list - Display a list of detected audio devices. You can use this to get the proper name of a device for use in the INI file.
* --schedule - Display the defined recording schedule (next 24 recordings by default)

When performing a manual recording (i.e., not based on the INI file) you can use the following options:

* --device - A device name from the --list command
* --rate - The sampling rate of the recording (e.g., 48000)
* --channels - The number of channels to record.
* --bit-depth - The bit depth to record (8, 16, 24)
* --duration - The duration, in hours, of each recording (defaults to one-hour)
* --protocol - Limit recording to only this protocol (all, nfc, or day)

Examples:

Get a list of recording devices:

```shell
> trecord --list
ID    Rate       Ch   Name
[ 0]  44100.00    2   Microsoft Sound Mapper - Input
[ 1]  44100.00    2   Microphone (High Definition Aud
[ 2]  44100.00    0   Microsoft Sound Mapper - Output
[ 3]  44100.00    0   Speakers (High Definition Audio
[ 4]  44100.00    2   Primary Sound Capture Driver
[ 5]  44100.00    2   Microphone (High Definition Audio Device)
[ 6]  44100.00    0   Primary Sound Driver
[ 7]  44100.00    0   Speakers (High Definition Audio Device)
[ 8]  48000.00    0   Speakers (High Definition Audio Device)
[ 9]  44100.00    2   Microphone (High Definition Audio Device)
[10]  44100.00    0   Speakers (HD Audio Speaker)
[11]  44100.00    2   Microphone (HD Audio Microphone 2)
[12]  44100.00    0   Headphones ()
```

Get the upcoming recording schedule. It displays the important times in the local time zone, UTC, and the recording start times, stop times, and durations:

```shell
> trecord --schedule
Location Details
----------------------------------------------------------
Name      : North Carolina State Capitol Building
TimeZone  : US/Eastern
Latitude  : 35.780480199773415
Longitude : -78.63909694937483
Date      : 2026-01-04 14:50:54.971263

Time Zone: UTC
----------------------------------------------------------
Midnight          : 20260104 05:00:00 UTC
Astronomical Dawn : 20260104 10:53:47 UTC
Noon              : 20260104 17:00:00 UTC
Astronomical Dusk : 20260104 23:45:34 UTC

Time Zone: US/Eastern
----------------------------------------------------------
Midnight          : 20260104 00:00:00 EST
Astronomical Dawn : 20260104 05:53:47 EST
Noon              : 20260104 12:00:00 EST
Astronomical Dusk : 20260104 18:45:34 EST

DAY  2026-01-04 14:50:54-05:00  2026-01-04 15:00:00-05:00  0:09:06
DAY  2026-01-04 15:00:00-05:00  2026-01-04 16:00:00-05:00  1:00:00
DAY  2026-01-04 16:00:00-05:00  2026-01-04 17:00:00-05:00  1:00:00
DAY  2026-01-04 17:00:00-05:00  2026-01-04 18:00:00-05:00  1:00:00
DAY  2026-01-04 18:00:00-05:00  2026-01-04 18:45:34-05:00  0:45:34
NFC  2026-01-04 18:45:34-05:00  2026-01-04 19:00:00-05:00  0:14:26
NFC  2026-01-04 19:00:00-05:00  2026-01-04 20:00:00-05:00  1:00:00
NFC  2026-01-04 20:00:00-05:00  2026-01-04 21:00:00-05:00  1:00:00
NFC  2026-01-04 21:00:00-05:00  2026-01-04 22:00:00-05:00  1:00:00
NFC  2026-01-04 22:00:00-05:00  2026-01-04 23:00:00-05:00  1:00:00
NFC  2026-01-04 23:00:00-05:00  2026-01-05 00:00:00-05:00  1:00:00
NFC  2026-01-05 00:00:00-05:00  2026-01-05 01:00:00-05:00  1:00:00
NFC  2026-01-05 01:00:00-05:00  2026-01-05 02:00:00-05:00  1:00:00
NFC  2026-01-05 02:00:00-05:00  2026-01-05 03:00:00-05:00  1:00:00
NFC  2026-01-05 03:00:00-05:00  2026-01-05 04:00:00-05:00  1:00:00
NFC  2026-01-05 04:00:00-05:00  2026-01-05 05:00:00-05:00  1:00:00
NFC  2026-01-05 05:00:00-05:00  2026-01-05 05:53:56-05:00  0:53:56
DAY  2026-01-05 05:53:56-05:00  2026-01-05 06:00:00-05:00  0:06:04
DAY  2026-01-05 06:00:00-05:00  2026-01-05 07:00:00-05:00  1:00:00
DAY  2026-01-05 07:00:00-05:00  2026-01-05 08:00:00-05:00  1:00:00
DAY  2026-01-05 08:00:00-05:00  2026-01-05 09:00:00-05:00  1:00:00
DAY  2026-01-05 09:00:00-05:00  2026-01-05 10:00:00-05:00  1:00:00
DAY  2026-01-05 10:00:00-05:00  2026-01-05 11:00:00-05:00  1:00:00
DAY  2026-01-05 11:00:00-05:00  2026-01-05 12:00:00-05:00  1:00:00
```

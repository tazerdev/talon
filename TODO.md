# List of Potential FUture Enhancements

## talon
- Configure the checklist function to generate an eBird compatible CSV for importing several checklists at once.
- Add the ability to import audacity labels as observations (e.g., *_supplemental.txt, or *_talon.txt vs *_talon.csv)
- Get a list of all confirmed detections, then remove all audio clips and spectrograms except those.

## talon-gui
- Add a weather tab which will display all of the weather info, if available, for the time range of the confirmed detections.
- Add the ability to edit the config file via a preferences dialog.
- Add the ability to edit the filter list via a dialog.
- Add the ability to toggle the species filter on/off.
- Add the ability to flag an observation (including a note) so notable observations are easier to find.
- When launching talon-gui from a directory with a lot of WAV files the interface doesn't render completely. Figure out how to get it all to render, and then load the files.
- Sort detections list correctly when there are events from multiple years (e.g., 12/31/2025 & 01/01/2026)

## talonlib
- Improve TalonWAVFile to write GUANO data manually because GUANO relies on the wave module which doesn't support 32-bit float files.
- Improve TalonWAVFile to fix the data chunk size on files which were terminated abruptly (power off, data chunk reports 0 bytes)
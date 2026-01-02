# List of Potential FUture Enhancements

## talon
- Configure the checklist function to generate an eBird compatible CSV for importing several checklists at once.
- Add the ability to import audacity labels as observations (e.g., *_supplemental.txt, or *_talon.txt vs *_talon.csv)

## talon-gui
- Add a weather tab which will display all of the weather info, if available, for the time range of the confirmed detections.
- Add the ability to edit the config file via a preferences dialog.
- Add the ability to edit the filter list via a dialog.
- Add the ability to toggle the species filter on/off.
- Add the ability to flag an observation (including a note) so notable observations are easier to find.

## talonlib
- Improve TalonWAVFile to write GUANO data manually because GUANO relies on the wave module which doesn't support 32-bit float files.
- Improve TalonWAVFile to fix the data chunk size on files which were terminated abruptly (power off, data chunk reports 0 bytes)
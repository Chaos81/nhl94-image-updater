# nhl94-image-updater
 
 **NHL94 Genesis ROM Image Updater version 0.2**

This Python app will take image assets supplied, and import them into a Genesis NHL'94 ROM. It will also export the image assets from a Genesis NHL'94 ROM and store them in byte arrays. It is useful for exporting assets from a previous ROM and importing them into a new one.

The app is designed to update and export the following image data:

- Team Logo and Palette
- Team Rink Logo and Palette (also the Home Jersey Palette)
- Team Away Jersey Palette
- Banner and Palettes

There are 2 options to use:

**Before running, please make sure the team names and rosters are already set in the ROM!!**

1. Extract Images
    - Choose a ROM, set the number of active teams, and click the Extract Images button. The app will output a folder with the ROMs name containing image assets for each team (listed by team 
    abbreviation).
2. Import Images
    - The program will use the image asset data located in the import folder (listed by team abbreviation). It will only import the image assets that are present in the folder, and the program will notify you of which teams were updated, and which were not. Once done, it will ask you for a location and a name to save the modified ROM.


If using the source code, this app needs certain Python modules installed locally in order to run. It was written using Python 3.9.6:

- PyQt5

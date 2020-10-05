
# Warning: the code is compatible with Python 3 up to Python 3.7, but not with Python >= 3.8. 


# Visualisation-tool

Tool to classify lenses vs non lenses

Put all the fits files of the images you want to classify in the folder "files_to_visualize"
When all of the images are graded a csv file with the classifications will be saved automatically in the folder "classifications".
If you want to interrupt the session before the end of the classification, it is also possible to save manually the csv file via the menu.
The tool can also handle color images datacubes.
New: you can open the image in ds9 but you need to specify the path to your ds9 executable on line 26 before.

For the mosaic tool specify the randomseed in the command line. e.g.:
">python visualisation_mosaic_3band.py 3"



New version:

visualisation_2.py for 1 band images
visualisation_color color images datacube
The new version is compatible only with python 3.

Necessary modules for the new version:
- pandas
- kivy + kivy garden matplotlib


To obtain cutouts from the legacy survey a csv file with coordinates has to be stored in the folder csv_catalog

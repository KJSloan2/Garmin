import os
from os import listdir
from os.path import isfile, join
import shutil
######################################################################################
######################################################################################
def get_directories_in_directory(directory_path):
    directory_list = [f.path for f in os.scandir(directory_path) if f.is_dir()]
    return directory_list
######################################################################################
sourceDirectoryPath = r"PATH TO SOURCE DIRECTORY"
directories = get_directories_in_directory(sourceDirectoryPath)
targetDirectory = r"data/gpx/"
######################################################################################
for dir in directories:
	print(dir)
	files_ = [f for f in listdir(dir) if isfile(join(dir, f))]
	for f in files_:
		parse_f  = f.split(".")
		if parse_f[-1].lower() == "gpx":
			print(f)
			dirPath = os.path.join(sourceDirectoryPath, dir)
			sourceFPath = os.path.join(dirPath, f)
			shutil.copy(sourceFPath, targetDirectory)
######################################################################################
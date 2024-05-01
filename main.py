import os
import shutil
from datetime import datetime
import configparser

# Load the configuration file
config = configparser.ConfigParser()
config.read('settings.ini')  # Specify the full path if the file is not in the same directory

# Get the date format for subfolder names
date_format = config.get('Settings', 'date_format', fallback='%Y_%m_%d')

# Get all base directories from the config file
base_dirs = [config.get('Directories', key) for key in config['Directories']]


# Function to organize files by their modified dates into subfolders
def organize_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path):
            mod_time = os.path.getmtime(file_path)
            date_folder = datetime.fromtimestamp(mod_time).strftime(date_format)
            new_folder_path = os.path.join(directory, date_folder)

            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)

            shutil.move(file_path, os.path.join(new_folder_path, filename))


# Process each directory listed in the configuration
for base_dir in base_dirs:
    base_dir = base_dir.strip()
    if os.path.exists(base_dir):
        organize_files(base_dir)
        print(f"Files in {base_dir} have been organized into subfolders named by date using format {date_format}.")
    else:
        print(f"Directory does not exist: {base_dir}")


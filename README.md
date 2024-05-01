
# Folders Cleanup

## Overview
The Folders Cleanup script automatically sorts files in specified directories into subfolders named according to their last modified date. This tool is particularly useful for managing and organizing files systematically in work environments or personal projects.

## Features
- **Multiple Directories:** Can handle multiple directories as specified in the configuration file.
- **Custom Date Formats:** Supports customizable date formats for subfolder names.

## Requirements
- Python 3.x
- `configparser` library (usually included with Python)

## Installation
1. **Clone the repository or download the files:**
   ```bash
   git clone https://your-repository-url.com
   cd folders-cleanup
   ```

2. **Ensure Python is installed:**
   - Visit [Python's official site](https://www.python.org/downloads/) to download and install Python if not already installed.

3. **Set up the `settings.ini` configuration file:**
   - Modify `settings.ini` according to the directories you want to organize and the preferred date format for subfolder names.

## Configuration
### Settings.ini
The `settings.ini` file is used to configure the directories to be organized and the format of the subfolder names. Below is an example configuration:

```ini
[Settings]
date_format = %%Y%%m%%d

[Directories]
base_dir1 = Z:\Resilio Sync\Working
base_dir2 = C:\Another\Path
```

- **date_format:** Specify the date format used for naming subfolders. Remember to escape `%` with another `%`.
- **Directories:** Add as many directories as you need under the `[Directories]` section. Each directory should have a unique key.

## Usage
To run the script, navigate to the script directory in your terminal or command prompt, and execute:
```bash
python folders_cleanup.py
```

The script will process the files in the specified directories, moving them into subfolders named by their modified date according to the specified format.

## Example

### Before Running the Script
Suppose you have a folder named "Working" with the following files:

```
Working/
│
├── report.docx
├── presentation.pptx
├── data.csv
```

Each file has different modification dates:
- `report.docx` - Modified on 2024-04-20
- `presentation.pptx` - Modified on 2024-04-21
- `data.csv` - Modified on 2024-04-22

### After Running the Script
After running the script with the configuration to use the date format `YYYY-MM-DD`, the "Working" directory would be organized as follows:

```
Working/
│
├── 2024-04-20/
│   └── report.docx
├── 2024-04-21/
│   └── presentation.pptx
├── 2024-04-22/
    └── data.csv
```

Each file is moved into a subfolder named after its modification date, making it easy to locate files based on when they were last modified.

## Date Format Examples

The `date_format` setting in `settings.ini` allows you to customize how the subfolders are named based on the file's modification date. Below are some examples of different date formats you can use:

- **YYYY-MM-DD**: For a standard date format that includes the full year, month, and day.
  - Format string: `%%Y-%%m-%%d`
  - Example: `2024-04-20`

- **YYMMDD**: For a compact date format with a two-digit year.
  - Format string: `%%y%%m%%d`
  - Example: `240420`

- **MMM DD, YYYY**: For a more human-readable format with the abbreviated month name.
  - Format string: `%%b %%d, %%Y`
  - Example: `Apr 20, 2024`

- **DD-MM-YY**: A common European format with two-digit year.
  - Format string: `%%d-%%m-%%y`
  - Example: `20-04-24`

- **YYYY/MM/DD**: Using slashes instead of dashes to separate year, month, and day.
  - Format string: `%%Y/%%m/%%d`
  - Example: `2024/04/20`

Remember to escape each `%` character by doubling it in the `settings.ini` configuration to avoid interpolation errors.


## License
MIT License

## Contributing
Contributions to the project are welcome. Please fork the repository and submit a pull request with your changes.

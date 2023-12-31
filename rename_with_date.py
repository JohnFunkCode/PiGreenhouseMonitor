#!/usr/bin/env python

###
# Invoked with the following cron job to archive and reset the graph every day at 8:00am
# 0 8 * * * cd /home/pi/Documents/code/PiGreenhouseMonitor && python rename_with_date.py GreenHouseReadingsChart.png GreenHouseReadings.csv >/dev/null 2>&1

import os
import sys
from datetime import datetime

def rename_file_with_date(filename):
    # Get the current date in the format YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")

    # Extract the filename and extension
    filename_no_ext, extension = os.path.splitext(filename)

    # Construct the new filename with the appended date
    new_filename = f"{filename_no_ext}-{today}{extension}"

    # Rename the file
    os.rename(filename, new_filename)

    print(f"File successfully renamed to: {new_filename}")

if __name__ == "__main__":
    # Check if filenames are provided as arguments
    if len(sys.argv) < 2:
        print("Usage: python script.py <filename1> <filename2> ...")
        sys.exit(1)

    # Process each filename provided as an argument
    for filename in sys.argv[1:]:
        rename_file_with_date(filename)
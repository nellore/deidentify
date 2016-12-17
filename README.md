# deidentify

Tools for deidentifying LABS consortium data.

`date_eliminator.py` eliminates date fields from a directory of CSV files according to user input. We applied this script to LABS consortium data (in particular, the ASCII subdirectories from the LABS 2 CD) to remove surgery operation dates, which generally had the label `SURGDATE`. On a first run, this script looks in each CSV for every column that has at least one date and asks the user whether that column should be eliminated. Its output is a new directory of CSVs with the selected dates removed as well as a configuration file that allows reproducing the run.

Usage:
```
python date_eliminator.py -i /path/to/input/directory -o /path/to/output/directory
```

To reproduce our run, cat the configuration file "date_eliminator.conf" from this directory into the script, as in
```
cat date_eliminator.conf | python date_eliminator.py \
    -i "/path/to/Longitudinal Assessment of Bariatric Surgery (LABS-=2) Preliminary/ASCII Database" \
    -o /path/to/output/directory
```

# License
This software is licensed under the MIT License. See LICENSE for details.

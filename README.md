# deidentify

This repo contains tools for deidentifying LABS consortium data.

`date_eliminator.py` can eliminate years from date fields as well as all fields that are detected to contain days, months, and years from a directory of LABS 2 CSV files according to user input. We applied this script to LABS consortium data (in particular, the ASCII subdirectories from the LABS 2 CD) to remove date-related PHI as characterized in [this](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/) document. On a first run, the script looks in each CSV for every column that either (1) appears to participate in a date occurring in three consecutive columns or (2) contains a date in `mm/dd/yyyy` or `dd/mm/yyyy` format; it then asks the user whether, respectively (1) the column should be eliminated or (2) the month and day should be removed from every date in the column. Its output is a new directory of CSVs with adjusted and removed date fields as well as a configuration file that allows reproducing the run.

We used [PyPy](https://bitbucket.org/pypy/pypy) 5.6.0 to run `date_eliminator.py`.

Usage:
```
pypy date_eliminator.py -i /path/to/input/directory -o /path/to/output/directory
```

Most of our deidentification is reproducible. To perform reproducible steps, `cat` the configuration file [`date_eliminator.conf`](date_eliminator.conf) into the script, as in
```
cat date_eliminator.conf | pypy date_eliminator.py \
    -i "/path/to/Longitudinal Assessment of Bariatric Surgery (LABS-2) Preliminary/ASCII Database" \
    -o /path/to/output/directory
```
All months and days were removed except for `FORMV` fields, where dates simply identified form versions.

We handled `SW_MINUTE.csv` and `SW_SUMMARY.csv` separately. In particular, in `SW_MINUTE.csv`, we preserved days since some first date in the `CPTRDATE` field so users can recover time series. To reproduce our deidentification of these files, run
```
pypy sw_edit.py -i /path/to/input/directory -o /path/to/output/directory
```
using the same input and output directories as for `date_eliminator.py`.

After running both `date_eliminator.py` and `sw_conf.py`, we navigated to `/path/to/output/directory` and ran
```
for i in $(ls | grep -v SW_); do echo $i; echo '*****'; cut -d',' -f2- $i \
    | grep "[0-9][0-9]*\-[0-9][0-9]*"; done | less
```
and
```
for i in $(ls | grep -v SW_); do echo $i; echo '*****'; cut -d',' -f2- $i \
    | grep "[0-9][0-9]*/[0-9][0-9]*"; done | less
```
to search for residual expressions of the form `[NUMBER]/[NUMBER]` and `[NUMBER]-[NUMBER]` in all fields besides `FORMV`. We uncovered many instances corresponding to dates in free text fields, and we used [Sublime Text 3](https://www.sublimetext.com/) to replace them with the text "[REDACTED]". We also manually inspected `DIB.csv` and `RSI.csv`, using Sublime Text to replace potentially identifying keywords from occupations in the `EMPS` field and study withdrawal reasons in the `*REAS*` fields with the text "[REDACTED]". Including scripts to reproduce these replacements would have required putting identifying information in this repo, which explains why our results are only partially reproducible.

# License
This software is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.

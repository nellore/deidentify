#!/usr/bin/env python
"""
date_eliminator.py

Eliminates date fields from a directory of CSV files according to user input.
We applied this script to LABS consortium data (in particular, ASCII
subdirectories from the LABS 2 CD)  to remove surgery operation dates. On a
first run, the script looks in each CSV for every column that has at least one
date and asks the user whether that column should be eliminated. Its output is
a new directory of CSVs with the selected dates removed as well as a
configuration file that permits reproducing the run.

To reproduce the run, cat the configuration file "date_eliminator.conf" written
to the output directory into the script.
"""
import argparse
import sys
import os
import csv
from glob import glob
from dateutil.parser import parse

def is_date(field):
    """ Checks if a field is a date 

        field: string

        Return value: True iff Python successfully parses date
    """
    try: 
        parse(field)
        return True
    except ValueError:
        return False

def yes_no_question(self, question, yes=False):
    """ Gets a yes/no answer from the user if self.yes is not True.

        question: string with question to be printed to console
        yes: automatically answers yes to question

        Return value: boolean
    """
    if yes:
        print '%s [y/n]: y' % question
        return True
    else:
        print '%s [y/n]: n' % question
        return False
    while True:
        sys.stdout.write('%s [y/n]: ' % question)
        try:
            try:
                return strtobool(raw_input().lower())
            except KeyboardInterrupt:
                sys.stdout.write('\n')
                sys.exit(0)
        except ValueError:
            sys.stdout.write('Please enter \'y\' or \'n\'.\n')

if __name__ == '__main__':
    # Print file's docstring if -h is invoked
    parser = argparse.ArgumentParser(description=__doc__, 
                formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--input-dir', '-i', type=str, required=True,
            help='input directory; all files in it are considered'
        )
    parser.add_argument('--output-dir', '-o', type=str, required=True,
            help='output directory'
        )
    parser.add_argument('--yes', '-y', action='store_const', const=True,
            default=False,
            help='answers "yes" to all questions; this eliminates all dates '
                 'found'
        )
    args = parser.parse_args()
    args.format = args.format.lower()
    try:
        os.makedirs(args.output_dir)
    except OSError as e:
        if e.errno != e.EEXIST:
            raise
    # Use sorted input file list to ensure reproducibility
    csv_list = sorted(glob(os.path.join(args.input_dir, '*')))
    with open(
            os.path.join(args.output_dir, 'date_eliminator.conf'), 'w'
        ) as conf_stream:
        for csv in input_csv_list:
            with open(csv) as csv_stream:
                dialect = csv.Sniffer().sniff(csv_stream.read(1024))
                csv_stream.seek(0)
                csv_reader = csv.reader(csv_stream, dialect)
                header = csv_reader.next()
                date_columns = set()
                # Get all columns with dates and store in date_columns
                for tokens in csv_stream:
                    for i, token in enumerate(tokens):
                        if is_date(token):
                            date_columns.add(i)
                to_eliminate = set()
                # Ask user which columns to eliminate and store in to_eliminate
                for index in date_columns:
                    if yes_no_question(
                            ('Eliminate all dates corresponding to field "{}" '
                             'in file "{}"?').format(header[index], csv)
                        ):
                        print >>conf_stream, 'y'
                        to_eliminate.add(index)
                    else:
                        print >>conf_stream, 'n'
                # Write final columns to same filename in output directory
                csv_stream.seek(0)
                with open(
                        os.path.join(args.output_dir, os.path.basename(csv)),
                        'w'
                    ) as output_stream:
                    csv_writer = csv.writer(output_stream, dialect)
                    for row in csv_reader:
                        csv_writer.writerow([
                                token for i, token in enumerate(row)
                                if i not in to_eliminate
                            ])
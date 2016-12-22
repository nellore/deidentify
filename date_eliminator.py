#!/usr/bin/env python
"""
date_eliminator.py

Eliminates months and days from date fields from a directory of CSV files
according to user input. We applied this script to LABS consortium data
(in particular, ASCII subdirectories from the LABS 2 CD) to remove identifying
information. On a first run, the script looks in each CSV for every column
that has at least one date and asks the user whether that column's month/day
should be eliminated. Its output is a new directory of CSVs with the selected
days/months from dates removed, a configuration file (date_eliminator.conf)
that permits reproducing the run, and a TSV (eliminated_fields.tsv) whose
first column lists fields removed or stripped of days/months and whose second
column lists the corresponding files from which the fields were adjusted or
eliminated.

To reproduce the run, cat the configuration file "date_eliminator.conf" written
to the output directory into the script.

This software is licensed under the MIT License.

Copyright (c) 2016 Abhinav Nellore

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import argparse
import sys
import os
import csv
import datetime
from glob import glob
from distutils.util import strtobool
import errno

_date_formats = ['%m/%d/%Y', '%d/%m/%Y']

def is_date(field):
    """ Checks if a field is a date 

        field: string

        Return value: True iff Python successfully parses date
    """
    for date_format in _date_formats:
        try:
            datetime.datetime.strptime(field, date_format)
            return True
        except ValueError:
            pass
    return False

def yes_no_question(question, yes=False):
    """ Gets a yes/no answer from the user if self.yes is not True.

        question: string with question to be printed to console
        yes: automatically answers yes to question

        Return value: boolean
    """
    if yes:
        print '%s [y/n]: y' % question
        return True
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
    parser.add_argument('--exceptions', type=str, nargs='+', required=False,
            help=('space-separated list of field names that should be '
                  'eliminated no matter what')
        )
    args = parser.parse_args()
    if args.exceptions is None:
        args.exceptions = []
    args.exceptions = set(args.exceptions)
    try:
        os.makedirs(args.output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    # Use sorted input file list to ensure reproducibility
    csv_list = sorted(glob(os.path.join(args.input_dir, '*')))
    with open(
            os.path.join(args.output_dir, 'date_eliminator.conf'), 'w'
        ) as conf_stream, open(
            os.path.join(args.output_dir, 'adjusted_fields.tsv'), 'w'
        ) as adjust_stream:
        print >>adjust_stream, (
                'adjusted field\tfilename\twas the field removed completely '
                '(0) or tweaked (1) to eliminate just the day and the month '
                'from a year?' 
            )
        for csv_file in csv_list:
            with open(csv_file) as csv_stream:
                try:
                    dialect = csv.Sniffer().sniff(csv_stream.read(1000000))
                except csv.Error as e:
                    print >>sys.stderr, (
                            'Could not determine delimiter for "{}"; '
                            'skipping....'
                        ).format(csv_file)
                csv_stream.seek(0)
                csv_reader = csv.reader(csv_stream, dialect)
                header = csv_reader.next()
                eliminable_columns, tweakable_columns = set(), set()
                # Get all columns with date information
                for tokens in csv_reader:
                    for i, token in enumerate(tokens):
                        if is_date(token) or token in args.exceptions:
                            tweakable_columns.add(i)
                        elif is_date('/'.join(tokens[i:i+3])):
                            eliminable_columns.update([i, i+1, i+2])
                to_eliminate, to_tweak = set(), set()
                # Ask user which columns to remove or adjust
                for index in sorted(list(eliminable_columns)):
                    if yes_no_question(
                            'Eliminate field "{}" in file "{}"?'.format(
                                    header[index], csv_file
                                ),
                            yes=args.yes
                        ):
                        print >>conf_stream, 'y'
                        print >>adjust_stream, '\t'.join(
                                [header[index], os.path.basename(csv_file),
                                    '0']
                            )
                        to_eliminate.add(index)
                    else:
                        print >>conf_stream, 'n'
                for index in sorted(list(tweakable_columns)):
                    if yes_no_question(
                            ('Remove day and month from every date '
                             'corresponding to field "{}" in file '
                             '"{}"?').format(header[index], csv_file),
                            yes=args.yes
                        ):
                        print >>conf_stream, 'y'
                        print >>adjust_stream, '\t'.join(
                                [header[index], os.path.basename(csv_file),
                                    '1']
                            )
                        to_tweak.add(index)
                    else:
                        print >>conf_stream, 'n'
                # Write final columns to same filename in output directory
                csv_stream.seek(0)
                with open(
                        os.path.join(
                                args.output_dir, os.path.basename(csv_file)
                            ), 'w'
                    ) as output_stream:
                    csv_writer = csv.writer(output_stream, dialect)
                    for row in csv_reader:
                        csv_writer.writerow([
                                tokens[i] if i not in to_eliminate
                                    else (tokens[i].rpartition('/')[-1]
                                           if i in to_tweak else tokens[i])
                                    for i in xrange(len(row))
                            ])

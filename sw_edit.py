#!/usr/bin/env python
"""
sw_edit.py

Deidentifies SW_SUMMARY.csv and SW_MINUTE.csv in LABS 2 data; these files  
cannot be deidentified properly by date_eliminator.py. This script replaces
dates with days since first day.

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
import errno
import itertools

_date_formats = ['%m/%d/%Y', '%d/%m/%Y']

if __name__ == '__main__':
    # Print file's docstring if -h is invoked
    parser = argparse.ArgumentParser(description=__doc__, 
                formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--input-dir', '-i', type=str, required=True,
            help=('input directory; should contain SW_MINUTE.csv and '
                  'SW_SUMMARY.csv')
        )
    parser.add_argument('--output-dir', '-o', type=str, required=True,
            help='output directory'
        )
    args = parser.parse_args()
    try:
        os.makedirs(args.output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    # Use sorted input file list to ensure reproducibility
    with open(
                os.path.join(args.input_dir, 'SW_MINUTE.csv')
            ) as minute_stream, open(
                os.path.join(args.output_dir, 'SW_MINUTE.csv'), 'w'
            ) as output_stream:
        try:
            dialect = csv.Sniffer().sniff(minute_stream.read(1000000))
        except csv.Error as e:
            print >>sys.stderr, (
                    'Could not determine delimiter for SW_MINUTE.csv; '
                    'skipping....'
                )
        minute_stream.seek(0)
        csv_reader = csv.reader(minute_stream, dialect)
        # Print header
        print >>output_stream, ','.join(csv_reader.next())
        for key, group in itertools.groupby(csv_reader, lambda x:x[0]):
            zero_date = None
            for tokens in group:
                if zero_date is None:
                    zero_date = datetime.datetime.strptime(tokens[7],
                                                                '%m/%d/%Y')
                print >>output_stream, ','.join(tokens[:6] + [
                        tokens[6].partition('-')[0] + (
                            (' ' + ' '.join(tokens[6].split(' ')[-2:]))
                            if tokens[6].endswith('M') else ''), str(
                                (datetime.datetime.strptime(tokens[7],
                                                                '%m/%d/%Y')
                                 - zero_date).days
                            )
                    ] + tokens[8:])
    with open(
                os.path.join(args.input_dir, 'SW_SUMMARY.csv')
            ) as summary_stream, open(
                os.path.join(args.output_dir, 'SW_SUMMARY.csv'), 'w'
            ) as output_stream:
        try:
            dialect = csv.Sniffer().sniff(summary_stream.read(1000000))
        except csv.Error as e:
            print >>sys.stderr, (
                    'Could not determine delimiter for SW_SUMMARY.csv; '
                    'skipping....'
                )
        csv_stream.seek(0)
        csv_reader = csv.reader(summary_stream, dialect)
        ''' Print header; note field 8 is excluded because it's day of week,
        which is more specific than year.'''
        print >>output_stream, ','.join([token for i, token in enumerate(
                csv_reader.next()
            ) if i != 8])
        for tokens in csv_reader:
            print ','.join(tokens[:6] + [
                        tokens[6].rpartition('/')[-1],
                        tokens[7].rpartition('/')[-1]
                    ] + tokens[9:]
                )

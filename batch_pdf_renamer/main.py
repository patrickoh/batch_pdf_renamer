# -*- coding: utf-8 -*-
"""
Created on 21 nov 2015

@author: Felipe M. Vieira <fmv1992@gmail.com>

Description:

main code
"""
# imports
import logging
import argparse
# TODO fix this import heresy '*'
from batch_pdf_renamer import *  # the module uses all functions
from datetime import datetime as dt  # for logging on the restore-file

# Parsing
parser = argparse.ArgumentParser()
parser.add_argument('--verbose', help='puts the program in verbose mode',
                    action="store_true", default=False)
parser.add_argument('--dry-run', help='makes no actual changes, just print    \
                                      them to stdout',
                    action="store_true", default=False)
parser.add_argument('--input', help='input file or folder to work on',
                    action="store", default='', required=True)
parser.add_argument('--restore-file', help='log file for easy undo',
                    action="store",
                    default=str(os.path.dirname(os.path.dirname(
                                os.path.abspath(__file__))) +
                                '/' + 'restorelog.txt'),
                    required=False)
parser.add_argument('--use-metadata', help='uses metadata embedded on pdf file\
                                           for renaming',
                    action="store_true", default=False, required=False)
args = parser.parse_args()
# Logging
if args.verbose is True:
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s',
                        level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S')
# Sample log
# logging.info('File %s already exists. Skipping.', 'string')
if args.use_metadata is True:
    logging.info('Using pdf metadata.')
else:
    logging.info('Not using pdf metadata. ISBN queries only.')
# Safety file for undoing
if not os.path.isfile(args.restore_file):
    raise Exception(str(args.restore_file + ' does not exist yet.'))
if args.dry_run is False:
    safe_log_file = open(str(os.path.dirname(os.path.dirname(
                             os.path.abspath(__file__)))
                         + '/' + 'restorelog.txt'),
                         'at')
    safe_log_file.write(str(dt.now()) + '\n')
else:
    logging.info('This is a dry run.')
    safe_log_file = None

# scan for pdfs
all_pdf_paths = scan_pdf_files_in_folder(args.input)
# extract metadata
for each_pdf in all_pdf_paths:
    # get metadata from isbn
    valid_isbn = get_isbn_from_file(each_pdf)
    if valid_isbn:
        metadata = get_metadata_from_valid_isbn(valid_isbn)
        if metadata:
            new_filename = work_on_title(metadata[0]) + '_-_' \
                + work_on_author(metadata[1]) + '.pdf'
            do_rename(each_pdf, new_filename, safe_log_file, args.dry_run)
            continue
    else:
        logging.info('Could not get a valid isbn for %s .',
                     os.path.basename(each_pdf))
    # get metadata from file
    if args.use_metadata is False:
        continue
    try:
        metadata = get_metadata_from_file(each_pdf)
        if metadata[0] is None or metadata[1] is None:
            pass
        elif metadata[0] == '' or metadata[1] == '':
            pass
        else:
            # do the renaming
            new_filename = work_on_title(metadata[0]) + '_-_' \
                + work_on_author(metadata[1]) + '.pdf'
            do_rename(each_pdf, new_filename, safe_log_file, args.dry_run)
    except:
        pass
if safe_log_file:
    safe_log_file.close()

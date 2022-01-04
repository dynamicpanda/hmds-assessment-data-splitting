#!/usr/bin/env python

"""Description: This script provides the ability to group records in an input
file into groups contained in JSON files.

Grouping is done based on several criteria:
    1. Records with the same address are combined into a single record.
        a. Each combined record's sequence ID is stored along with the main
        record's data.
    2. Records are grouped according to their GROUP and COUNTRY values,
    respectively.
    3. Records are sorted by sequence ID.

Output data is stored in as JSON in two ways:
    1. As one JSON file containing all sorted and grouped records.
    2. As individual JSON files defined by GROUP and COUNTRY values.
"""

# Standard Library imports
import csv
import logging
import json
import os
import socket
import sys

from collections import defaultdict

# set up basic logging to print to the console
logging.getLogger().setLevel(logging.DEBUG)

# define constants
DELIMITER = ','
JSON_EXT = '.json'
FINAL_JSON_NAME = 'final' + JSON_EXT
OUTPUT_LOCATION = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../results'
)


class Record(dict):

    def __init__(self, sequence_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__sequence_id = sequence_id
        self.sub_ids = defaultdict(set)

    @property
    def sequence_id(self):
        """Get the sequence ID of this record

        :return: The sequence ID of the record
        :rtype: str
        """
        return self.__sequence_id

    def merge(self, other_record):
        """Merge the record provided into this record. Prioritize the data of
        this record when data differs.
        TODO: Clarify these requirements. Should different data always be
        accepted?
        TODO: Should merges be handled as a natural join? outer?

        :param other_record: The record to merge into this one.
        :type other_record: Record
        """
        self.sub_ids.add(other_record.sequence_id)


class RecordList(list):
    def merge(self, main_record_index, *merge_indices):
        """Merge the records in the positions provided, preserving the first
        record and removing all others.

        :param main_record_index: The index of the main record into which the
        other(s) will be merged.
        :type main_record_index: int
        :param merge_indices: The indices in the list of the records which will
        be merged into the main record.
        :type merge_indices: tuple
        """

        # merge and remove all provided records
        for index in merge_indices:
            self[main_record_index].merge(self.pop(index))


if __name__ == '__main__':
    logging.info(f'Starting {__file__} on {socket.gethostname()}...')

    try:
        csv_path = sys.argv[1]
        logging.info(f'Processing file {csv_path}...')

        if not os.path.isdir(OUTPUT_LOCATION):
            os.makedirs(OUTPUT_LOCATION)

        # read the records from the CSV file
        with open(csv_path, newline='', encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=DELIMITER)
            all_records = {}

            # generate a record object for each row in the CSV file
            for row in reader:
                logging.debug(f'Row: {row}')
                record = Record(row['SEQUENCE_ID'], **row)
                logging.debug(f'Record: {record}')
                all_records[record.sequence_id] = record

        # dump the records into the final JSON file
        final_json_path = os.path.join(OUTPUT_LOCATION, FINAL_JSON_NAME)
        with open(final_json_path, 'w') as final_json_file:
            json.dump(all_records, final_json_file, indent=4)

    except Exception:
        logging.exception(f'Exception occurred while processing {csv_path}')
    else:
        logging.info(f'{__file__} ended successfully')

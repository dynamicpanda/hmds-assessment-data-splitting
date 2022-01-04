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
import pprint
import socket
import sys

from collections import defaultdict

# set up basic logging to print to the console
logging.getLogger().setLevel(logging.DEBUG)

# define constants
ADDRESS_FIELDS = ('STREET', 'CITY', 'ZIP', 'COUNTRY')
DELIMITER = ','
GROUP_BY_FIELDS = ('GROUP', 'COUNTRY')
JSON_EXT = '.json'
FINAL_JSON_NAME = 'final' + JSON_EXT
OUTPUT_LOCATION = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../results'
)


class Record(dict):
    """Class representing a record, namely that in a batch. All records
    include sequence IDs and other supplemental data which may be stored in the
    Record object like any other dictionary.
    """

    def __init__(self, sequence_id, *args, **kwargs):
        """Initialize the Record with sequence ID and any starting dictionary
        data.

        :param sequence_id: The sequence ID identifying the record
        :type sequence_id: str
        """
        super().__init__(*args, **kwargs)

        self['SEQUENCE_ID'] = sequence_id
        self['MERGED_SEQUENCE_IDS'] = []

    @property
    def sequence_id(self):
        """Get the sequence ID of this record

        :return: The sequence ID of the record
        :rtype: str
        """
        return self['SEQUENCE_ID']

    @property
    def merged_sequence_ids(self):
        """Get the merged sequence IDs within this record

        :return: The merged sequenced IDs within the record
        :rtype: list
        """
        return self['MERGED_SEQUENCE_IDS']

    def merge(self, other_record):
        """Merge the record provided into this record. Prioritize the data of
        this record when data differs.

        :param other_record: The record to merge into this one.
        :type other_record: Record
        """
        self['MERGED_SEQUENCE_IDS'].append(other_record.sequence_id)


class Batch(dict):

    def add(self, record):
        """Add the record provided to the batch, using its sequence ID as the
        dictionary key.

        :param record: The record to add to the batch
        :type record: Record
        """

        if not isinstance(record, Record):
            raise TypeError(f'Invalid type: {type(record)}. Records must be '
                            'of \'Record\' type')

        self[record.sequence_id] = record

    def merge(self, main_record_id, *merge_ids):
        """Merge the records with the IDs provided into the main record with
        the main record ID provided, removing all merged records.

        :param main_record_id: The ID of the main record into which the
        other(s) will be merged.
        :type main_record_id: str
        :param merge_ids: The IDs in the batch of the records which will be
        merged into the main record.
        :type merge_ids: tuple
        """

        # merge and remove all provided records
        for merge_id in merge_ids:
            self[main_record_id].merge(self.pop(merge_id))


if __name__ == '__main__':
    logging.info(f'Starting {__file__} on {socket.gethostname()}...')

    try:
        csv_path = sys.argv[1]
        logging.info(f'Processing file {csv_path}...')

        batch = Batch()

        if not os.path.isdir(OUTPUT_LOCATION):
            os.makedirs(OUTPUT_LOCATION)

        # read the records from the CSV file
        with open(csv_path, newline='', encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=DELIMITER)

            # generate a record object for each row in the CSV file
            for row in reader:
                batch.add(Record(row['SEQUENCE_ID'], **row))
        logging.debug(f'Batch: {pprint.pformat(batch)}')

        # merge records with same address info
        addresses = defaultdict(set)
        for sequence_id in list(batch.keys()):
            # combine address fields as one string to act as a key
            record = batch[sequence_id]
            address = ''.join((record[field] for field in ADDRESS_FIELDS))
            addresses[address].add(sequence_id)

        # merge sequence IDs with like addresses into the record with the
        # lowest sequence ID
        for address, sequence_ids in addresses.items():
            if len(sequence_ids) > 1:
                sorted_sequence_ids = sorted(sequence_ids)
                main_record_id = sorted_sequence_ids[0]
                merge_record_ids = sorted_sequence_ids[1:]

                logging.info(f'Merging IDs {main_record_id} into record '
                             f'{merge_record_ids}...')
                batch.merge(main_record_id, *merge_record_ids)

        # dump the records into the final JSON file
        final_json_path = os.path.join(OUTPUT_LOCATION, FINAL_JSON_NAME)
        logging.info(f'Writing all records to {final_json_path}...')
        with open(final_json_path, 'w') as final_json_file:
            json.dump(batch, final_json_file, indent=4, sort_keys=True)

        # group batch by defined fields
        groups = defaultdict(Batch)
        for sequence_id, record in batch.items():
            key = tuple(record[field] for field in GROUP_BY_FIELDS)
            groups[key].add(record)
        logging.debug(f'Groups: {pprint.pformat(groups)}')

        # dump each group of records into its own JSON file
        for group, batch in groups.items():
            group_json_path = os.path.join(OUTPUT_LOCATION,
                                           '_'.join(group) + JSON_EXT)
            logging.info(
                f'Writing group {group} records to {group_json_path}...')
            with open(group_json_path, 'w') as group_json_file:
                json.dump(batch, group_json_file, indent=4, sort_keys=True)

    except Exception:
        logging.exception(f'Exception occurred while processing {csv_path}')
    else:
        logging.info(f'{__file__} ended successfully')

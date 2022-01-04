# HMDS Developer Assessment - Data Splitting

## Requirements
> ### Submission
> Code should be uploaded to your source control platform of choice (Gitlab/Github/Bitbucket) and made available to the hiring team. Follow the proper source control pipeline showing branching/commit/push/merge etc. Be prepared to discuss your thought process during the interview. Feel free to provide any other documentation you feel would be helpful.

> ### Data Splitting and Grouping
> Create a python solution to sort and manipulate the supplied data file csv according to the following criteria.
> 1.	Avoid using the Pandas Python Library.
> 2.	Use an object-oriented approach.
> 3.	Data should be converted to JSON using SEQUENCE_ID as a key.
> 4.	Data should be split into groups based on their GROUP identifiers.
> 5.	Data should be further split into groups based on COUNTRY identifiers.
> 6.	Records that have matching data for STREET, CITY, ZIP and COUNTRY should be grouped into the same SEQUENCE_ID. Using the lowest SEQUENCE_ID in the group. Create a new data point retaining the original SEQUENCE_ID of any grouped sub-entries.
> 7.	Once processing is finished the SEQUENCE_ID identifiers in each group should be sorted into ascending order.
> 8.	JSON groups should be output to files following the naming convention of GROUP_COUNTRY.json based on the data it contains.
>     a.	EX. A_Japan.json
> 9.	Output entire JSON structure to an output file named final.json
> 10.	Place output data within a results folder within the repository.

## Script Execution
Grouping is done based on several criteria:
1. Records with the same address are combined into a single record.
    a. Each combined record's sequence ID is stored along with the main
    record's data.
2. Records are grouped according to their GROUP and COUNTRY values,
respectively.
3. Records are sorted by sequence ID.

Output data is stored in as JSON in two ways:
- As one JSON file containing all sorted and grouped records.
- As individual JSON files defined by GROUP and COUNTRY values.

## Design
In keeping with an object-oriented approach, two classes are defined which inherit from base Python objects:
- **Record**, which inherits from dict and represents a record of data.
- **Batch**, which also inherits from dict and represents a batch of records.

Each object primarily contains methods for merging records. Grouping is accomplished easily enough by operating on the objects as dictionaries, so methods for grouping are not included in the classes.

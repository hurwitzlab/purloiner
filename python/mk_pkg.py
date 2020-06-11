#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@gmail.com>
Date   : 2020-01-09
Purpose: Make datapackage
"""

import argparse
import csv
import os
from datapackage import Package
from typing import NamedTuple, List, TextIO
from pprint import pprint


class Args(NamedTuple):
    data_file: List[TextIO]
    ontology_file: TextIO
    out_file: str
    missing_values: List[str]


# --------------------------------------------------
def get_args() -> Args:
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Make datapackage',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-d',
                        '--data',
                        metavar='FILE',
                        type=argparse.FileType('rt'),
                        nargs='+',
                        help='Input file')

    parser.add_argument('-o',
                        '--ontology',
                        metavar='FILE',
                        type=argparse.FileType('rt'),
                        help='Ontology file')

    parser.add_argument('-O',
                        '--outfile',
                        help='Output file',
                        metavar='FILE',
                        type=str,
                        default='datapackage.json')

    parser.add_argument('-m',
                        '--missing',
                        help='Missing value',
                        metavar='missing',
                        type=str,
                        nargs='*')

    parser.add_argument('-f',
                        '--force',
                        help='Force overwrite of existing --outfile',
                        action='store_true')

    args = parser.parse_args()

    if os.path.isfile(args.outfile) and not args.force:
        parser.error(f'--outfile "{args.outfile}" exists!'
                     'Use --force to overwrite')

    return Args(args.data, args.ontology, args.outfile, args.missing)


# --------------------------------------------------
def main() -> None:
    """Make a jazz noise here"""

    args = get_args()
    package = Package()
    ontology = get_ontology(args.ontology_file)

    for i, fh in enumerate(args.data_file, start=1):
        print(f'{i:3}: {os.path.basename(fh.name)}')
        fh.close()
        package.infer(fh.name)

    for res in package.resources:
        if args.missing_values:
            res.descriptor['schema']['missingValues'].extend(
                args.missing_values)

        for field in res.descriptor['schema']['fields']:
            name = field.get('name')
            if not name:
                continue

            ont = ontology.get(name)
            if not ont:
                continue

            data_type = ont.get('frictionless type', field.get('type'))
            if data_type:
                field['type'] = data_type

            data_format = ont.get('frictionless format', field.get('format'))
            if data_format:
                field['format'] = data_format

            rdf_type = ont.get('rdftype', field.get('rdftype'))
            if rdf_type:
                field['rdftype'] = rdf_type

            units = ont.get('units purl', field.get('pm:unitRdfType'))
            if units:
                field['pm:unitRdfType'] = units

            source_url = ont.get('pm:source url', field.get('pm:sourceUrl'))
            if source_url:
                field['pm:source url'] = source_url

            measure_source = ont.get('measurement source purl',
                                     field.get('pm:measurementSourceRdfType'))
            if measure_source:
                field['pm:measurementSourceRdfType'] = measure_source

            measure_url = ont.get('pm:measurement source protocol',
                                  field.get('pm:measurement source protocol'))
            if measure_url:
                field['pm:measurementSourceProtocolUrl'] = measure_url

            is_searchable = ont.get('pm:searchable', field.get('pm:searchable'))
            if is_searchable:
                field['pm:searchable'] = is_searchable

        package.remove_resource(res.name)
        package.add_resource(res.descriptor)

    package.save(args.out_file)

    print(f'Done, see "{args.out_file}"')


# --------------------------------------------------
def get_ontology(fh: TextIO):
    """ Read ontology file """

    return {r['parameter']: r for r in csv.DictReader(fh, delimiter='\t')}


# --------------------------------------------------
if __name__ == '__main__':
    main()

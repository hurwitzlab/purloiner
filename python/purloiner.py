#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@gmail.com>
Date   : 2020-06-10
Purpose: Add ontology terms
"""

import argparse
import csv
import os
import re
from pprint import pprint
import consolemenu
# from consolemenu.items import *
from typing import NamedTuple, List, TextIO, Optional


class Args(NamedTuple):
    fhs: List[TextIO]
    ontology_file: TextIO


class Term(NamedTuple):
    accession: str
    purl: str
    label: str
    units: str
    units_purl: str


class Column(NamedTuple):
    name: str
    term: Optional[Term]


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Add ontology terms',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-f',
                        '--file',
                        metavar='FILE',
                        help='Input file(s)',
                        type=argparse.FileType('rt'))

    parser.add_argument('-o',
                        '--ontology',
                        help='File of ontology terms',
                        metavar='FILE',
                        type=argparse.FileType('rt'))

    parser.add_argument('-O',
                        '--outdir',
                        help='Output directory',
                        metavar='DIR',
                        default=os.path.join(os.getcwd(), 'ontology'))

    return parser.parse_args()


# --------------------------------------------------
def main() -> None:
    """Make a jazz noise here"""

    args = get_args()
    terms = get_terms(args.ontology)

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    _, ext = os.path.splitext(args.file.name)
    delim = ',' if ext == '.csv' else '\t'
    reader = csv.DictReader(args.file, delimiter=delim)
    columns = [Column(name=c, term=None) for c in reader.fieldnames]

    while True:
        column = column_select(columns)
        print(column)
        if column is None:
            break

        term = term_select(columns[column], terms)
        if term is not None:
            columns[column] = columns[column]._replace(term=term)

    out_file = write_out(args.outdir, os.path.basename(args.file.name), columns)

    print(f'Done, wrote "{out_file}"')


# --------------------------------------------------
def get_terms(fh: TextIO) -> List[Term]:
    """ Get ontology terms from lookup file """

    reader = csv.DictReader(fh, delimiter='\t')
    required = ['PURL', 'PURL LABEL', 'UNIT LABEL', 'STANDARD UNIT PURL']
    missing = list(filter(lambda f: f not in reader.fieldnames, required))

    if missing:
        raise Exception('ontology file "{}" missing: {}'.format(
            fh.name, ', '.join(missing)))

    terms = []
    for rec in reader:
        purl = rec['PURL']
        match = re.search(r'([A-Z]{1,}_\d+)', purl)
        if match:
            terms.append(
                Term(match.group(1), rec['PURL'], rec['PURL LABEL'],
                     rec['UNIT LABEL'], rec['STANDARD UNIT PURL']))

    return terms


# --------------------------------------------------
def column_select(columns: List[Column]) -> Optional[int]:
    """ Select a column """

    menu = consolemenu.SelectionMenu('Select a column')

    items = []
    for column in columns:
        items.append('{}{}'.format(
            column.name,
            ' => "{}"'.format(column.term.accession) if column.term else ''))

    index = menu.get_selection(items)
    return index if index < len(items) else None


# --------------------------------------------------
def term_select(column: Column, terms: List[Term]) -> Optional[Term]:
    """ Get ontology term for column """

    menu = consolemenu.SelectionMenu(f'Select term for {column.name}')

    items = []
    for term in terms:
        items.append('{} ({})'.format(term.label, term.accession))

    index = menu.get_selection(items)
    return terms[index] if index < len(items) else None


# --------------------------------------------------
def write_out(out_dir: str, filename: str, columns: List[Column]) -> str:
    """ Write output file """

    fieldnames = [
        'parameter', 'rdf type purl label', 'rdf type purl', 'units label',
        'units purl', 'measurement source purl label',
        'measurement source purl', 'pm:measurement source protocol',
        'pm:source url', 'frictionless type', 'frictionless format'
    ]

    out_file = os.path.join(out_dir, filename)
    out_fh = open(out_file, 'wt')
    writer = csv.DictWriter(out_fh, delimiter='\t', fieldnames=fieldnames)
    writer.writeheader()
    for col in columns:
        writer.writerow({
            'parameter': col.name,
            'rdf type purl label': col.term.label if col.term else '',
            'rdf type purl': col.term.purl if col.term else '',
            'units label': col.term.units if col.term else '',
            'units purl': col.term.units_purl if col.term else '',
            'measurement source purl label': '',
            'measurement source purl': '',
            'pm:measurement source protocol': '',
            'pm:source url': '',
            'frictionless type': '',
            'frictionless format': ''
        })

    return out_file


# --------------------------------------------------
if __name__ == '__main__':
    main()

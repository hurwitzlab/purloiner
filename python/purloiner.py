#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@gmail.com>
Date   : 2020-06-10
Purpose: Add ontology terms
"""

import argparse
import consolemenu
import csv
import os
import re
import sys
from collections import defaultdict
from typing import NamedTuple, List, TextIO, Optional


class Args(NamedTuple):
    data_file: TextIO
    ontology_file: TextIO
    out_file: str
    assoc_file: Optional[TextIO]


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
def get_args() -> Args:
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Add ontology terms',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-f',
                        '--file',
                        metavar='FILE',
                        help='Input file(s)',
                        type=argparse.FileType('rt'),
                        required=True)

    parser.add_argument('-o',
                        '--ontology',
                        help='File of ontology terms',
                        metavar='FILE',
                        type=argparse.FileType('rt'),
                        required=True)

    parser.add_argument('-O',
                        '--outfile',
                        help='Output file',
                        metavar='FILE',
                        default='')

    parser.add_argument('-a',
                        '--assoc_file',
                        help='Previous association file',
                        metavar='FILE',
                        type=argparse.FileType('rt'))

    args = parser.parse_args()

    if not args.outfile:
        root, ext = os.path.splitext(args.file.name)
        args.outfile = root + '_ontology' + ext

    return Args(args.file, args.ontology, args.outfile, args.assoc_file)


# --------------------------------------------------
def main() -> None:
    """Make a jazz noise here"""

    args = get_args()

    if os.path.isfile(args.out_file):
        question = f'Output file "{args.out_file}" exists. Overwrite? [yN] '
        answer = input(question)
        if not answer.lower().startswith('y'):
            sys.exit('Bye!')

    terms = get_terms(args.ontology_file)
    columns = get_columns(args.data_file, args.assoc_file, terms)

    while True:
        column = column_select(columns)
        if column is None:
            break

        term = term_select(columns[column], terms)
        if term is not None:
            columns[column] = columns[column]._replace(term=term)

    write_out(args.out_file, columns)

    print(f'Done, wrote "{args.out_file}"')


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
    def fmt(column: Column):
        term = ''
        if column.term:
            term = ' => "{}" ({})'.format(column.term.accession,
                                          trunc(column.term.label, 40))
        return f'{column.name}{term}'

    items = list(map(fmt, columns))
    index = consolemenu.SelectionMenu.get_selection(items,
                                                    title='Select a column')
    return index if index < len(items) else None


# --------------------------------------------------
def term_select(column: Column, terms: List[Term]) -> Optional[Term]:
    """ Get ontology term for column """

    items = list(map(lambda t: f'{trunc(t.label, 45)} ({t.accession})', terms))
    index = consolemenu.SelectionMenu.get_selection(
        title=f'Select ontology term for "{column.name}"', strings=items)

    return terms[index] if index < len(items) else None


# --------------------------------------------------
def write_out(out_file: str, columns: List[Column]) -> None:
    """ Write output file """

    answer = input(f'OK to write "{out_file}"? [Yn] ')
    if answer and answer.lower()[0] == 'n':
        print('Will not write output file!')
        return

    fieldnames = [
        'parameter', 'rdf type purl label', 'rdf type purl', 'units label',
        'units purl', 'measurement source purl label',
        'measurement source purl', 'pm:measurement source protocol',
        'pm:source url', 'frictionless type', 'frictionless format'
    ]

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

    return None


# --------------------------------------------------
def get_columns(data_fh: TextIO, assoc_fh: Optional[TextIO],
                terms: List[Term]) -> List[Column]:
    """ Read input file, maybe merge former associations """

    term_dict = {term.purl: term for term in terms}

    assoc = defaultdict(str)
    if assoc_fh:
        reader = csv.DictReader(assoc_fh, delimiter='\t')
        reqd = ['parameter', 'rdf type purl']
        missing = list(filter(lambda f: f not in reader.fieldnames, reqd))
        if missing:
            msg = 'Assoc file "{fh.name}" missing: {", ".join(missing)}'
            raise Exception(msg)

        for rec in reader:
            term = term_dict.get(rec['rdf type purl'])
            if term:
                assoc[rec['parameter']] = term

    _, ext = os.path.splitext(data_fh.name)
    delim = ',' if ext == '.csv' else '\t'
    reader = csv.DictReader(data_fh, delimiter=delim)
    return [Column(name=col, term=assoc.get(col)) for col in reader.fieldnames]


# --------------------------------------------------
def trunc(text: str, max_len: int):
    """ Truncate a string to a maximum length """

    return text[:max_len - 3] + '...' if len(text) > max(3, max_len) else text


# --------------------------------------------------
def test_trunc():
    """ Test trunc """

    assert trunc('', 3) == ''
    assert trunc('foo', 3) == 'foo'
    assert trunc('foobar', 6) == 'foobar'
    assert trunc('foobar', 5) == 'fo...'


# --------------------------------------------------
if __name__ == '__main__':
    main()

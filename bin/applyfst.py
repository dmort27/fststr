#!/usr/bin/env python

import argparse
from os import error
import pywrapfst as fst
from fststr import fststr
import sys
import itertools

def compile(fst_file):
    st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
    compiler = fst.Compiler(
        isymbols=st, osymbols=st,
        keep_isymbols=True, keep_osymbols=True)
    with open(fst_file) as f:
        for word in f:
            print(word.strip(), file=compiler)
    return compiler.compile()

def apply(args):
    fst = compile(args.fst)
    if args.input:
        with open(args.input) as f:
            words = [w.strip() for w in f]
    elif args.string:
        print('args.string=', args.string)
        words = [args.string]
    else:
        print('No words provided')
        sys.exit()
    return words, [fststr.apply(w, fst) for w in words]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fst', help='AT&T FST file to apply')
    parser.add_argument('-i', '--input', help='Input file (one item per line)')
    parser.add_argument('-S', '--string', help='Input string')
    args = parser.parse_args()
    inputs, outputs = apply(args)
    print(outputs)
    for inp, ws in zip(inputs, outputs):
        print(inp, '->', ', '.join(ws))

if __name__ == '__main__':
    main()
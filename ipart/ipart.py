#!/bin/python3
# By Mattias Sjö, 2024-25
#
# Computes integer partitions
# Run with argument --help for more instructions
#
# Generates the partitions in lexicographic order using a straightforward recursive algorithm with caching.
# Prints them to the screen and prepares a form file called partitions/(summary of arguments).hf

import argparse
from datetime import datetime
from functools import cache
from os import makedirs
from sys import argv

from condIO import CondIO

# These three implemetations are very similar, but a bit of code repitition is clearer
# than the various conditionals needed to fit all in one function

@cache
def _upart(tot, filter):
    if tot <= 0:
        return [[]]
    heads = [n+1 for n in range(tot) and filter(n+1)]
    return [[head] + tail
                for head in reversed(heads)
                for tail in _upart(tot-head, filter)]

def upart(integer, filter=lambda x: True):
    """
    Compute an unordered integer partition.

    Arguments:
    integer -- the nonnegative integer to be partitioned
    filter -- a boolean function; only values for which it is True are allowed in partitions.
        (default: unconditionally true)

    Returns:
    A list containing all lists of positive integers such that sum(list) = integer
    They are ordered lexicographically; thus, the first one is [tot] and the last is [1]*tot.
    If integer is 0, then the result is [].
    """
    if integer < 0:
        raise ValueError(f"Integer must be non-negative ({integer} provided)")
    return _upart(integer, filter)


@cache
def _opart(tot, maxpart, filter):
    if tot <= 0:
        return [[]]
    heads = [n+1 for n in range(min(maxpart,tot)) if filter(n+1)]
    return [[head] + tail
                for head in reversed(heads)
                for tail in _opart(tot-head, head, filter)]
def opart(integer, filter=lambda x: True):
    """
    Compute an ordered integer partition.

    Arguments:
    integer -- the nonnegative integer to be partitioned
    filter -- a boolean function; only values for which it is True are allowed in partitions.
        (default: unconditionally true)

    Returns:
    A list containing all (descendingly) sorted lists of positive integers such that sum(list) = integer.
    They are ordered lexicographically; thus, the first one is [integer] and the last is [1]*integer.
    If integer is 0, then the result is [].
    """
    if integer < 0:
        raise ValueError(f"Integer must be non-negative ({integer} provided)")
    return _opart(integer, integer, filter)
    
@cache
def _ufpart(tot, length):
    if length <= 0:
        return [[]]
    if length == 1:
        return [[tot]]
    heads = [n for n in range(tot+1) if filter(n)]
    return [[head] + tail
                for head in reversed(heads)
                for tail in _ufpart(tot-head, length-1, filter)]

def ufpart(integer, length, filter=lambda x: True):
    """
    Compute an unordered fixed-length unordered integer partition.

    Arguments:
    integer -- the nonnegative integer to be partitioned
    length -- the length of the partition
    filter -- a boolean function; only values for which it is True are allowed in partitions.
        (default: unconditionally true)

    Returns:
    A list containing all lists of nonnegative integers such that sum(list) = integer and len(list) = integer.
    They are ordered lexicographically; thus, the first one is [integer]+[0]*(length-1) and the last is the reverse of that.
    If integer is 0, then the result is [[0]].
    If length is 0 (and integer is not), then the result is [].
    """
    if integer < 0:
        raise ValueError(f"Integer must be non-negative ({integer} provided)")
    if length < 0:
        raise ValueError(f"Length must be non-negative ({length} provided)")
    if length == 0:
        return [] if integer > 0 else [[]]
    return _ufpart(integer, length, filter)

@cache
def _ofpart(tot, maxpart, length, filter):
    if length <= 0:
        return [[]]
    if length == 1:
        return [[tot]]
    if maxpart == 0:
        return [[0]*length] # short-circuit
    heads = [n for n in range(min(tot,maxpart)+1) if tot <= n*length and filter(n)] # condition ensures a tail exists
    return [[head] + tail
                for head in reversed(heads)
                for tail in _ofpart(tot-head, head, length-1, filter)]

def ofpart(integer, length, filter=lambda x: True):
    """
    Compute an ordered fixed-length unordered integer partition.

    Arguments:
    integer -- the nonnegative integer to be partitioned
    length -- the length of the partition
    filter -- a boolean function; only values for which it is True are allowed in partitions.
        (default: unconditionally true)

    Returns:
    A list containing all (descendingly) sorted lists of nonnegative integers such that sum(list) = integer and len(list) = integer.
    They are ordered lexicographically; thus, the first one is [integer]+[0]*(length-1) and the last is the reverse of that.
    If integer is 0, then the result is [[0]].
    If length is 0 (and integer is not), then the result is [].
    """
    if integer < 0:
        raise ValueError(f"Integer must be non-negative ({integer} provided)")
    if length < 0:
        raise ValueError(f"Length must be non-negative ({length} provided)")
    if length == 0:
        return [] if integer > 0 else [[]]
    return _ofpart(integer, integer, length, filter)

def main(argv):

    # Parse arguments
    parser = argparse.ArgumentParser(
        prog='ipart',
        formatter_class=argparse.RawTextHelpFormatter,
        description="Utility for generating integer partitions.\nBy Mattias Sjö, 2025",
        epilog="The mode options -[ou] are mutually exclusive, and either may be combined with -f.\nMore than one of the output options -[stcF] may be used simultaneously.\n \nThis uses a straightforward non-lazy recursive algorithm that, thanks to extensive caching, should be more-or-less linear in the number of partitions, which is in turn exponential in INT even in the --ordered case.")

    part_mode = parser.add_argument_group("partition modes")
    excl_mode = part_mode.add_mutually_exclusive_group()
    excl_mode.add_argument('-o', '--ordered', action='store_true',
                           help="Generate ordered partitions into positive integers. This is the default.")
    excl_mode.add_argument('-u', '--unordered', action='store_true',
                           help="Generate unordered partititons into positive integers.")

    part_mode.add_argument('-f', '--fixed', action='store', nargs=1, type=int, metavar='N',
                           help="Instead of a flexible number of positive integers, generate partitions into a fixed number N of non-negative integers.")

    modifiers = parser.add_argument_group("partition modifiers")
    modifiers.add_argument('-m', '--min', action='store', nargs=1, type=int, metavar='N',
                           help="Only generate partitions whose smallest element is greater or equal to N. Values less than 1 (or 0 with -f) are never considered.")
    modifiers.add_argument('-M', '--max', action='store', nargs=1, type=int, metavar='N',
                           help="Only generate partitions whose largest element is less or equal to N.")
    parity = modifiers.add_mutually_exclusive_group()
    parity.add_argument('-e', '--even', action='store_true',
                           help="Only generate partitions into even integers. There will be none if INTEGER is odd.")
    parity.add_argument('-E', '--odd', action='store_true',
                           help="Only generate partitions into odd integers.")

    out_mode = parser.add_argument_group("output options")
    out_mode.add_argument('-s', '--std', action='store_true',
                      help="Output whitespace-separated partitions to stdout, one per line. This is implied if no other output mode is specified.")
    out_mode.add_argument('-t', '--txt', action='store_true',
                      help="Output whitespace-separated partitions to partitions/FILE.txt, one per line. FILE is determined by the other options.")
    out_mode.add_argument('-c', '--csv', action='store_true',
                      help="Output comma-separated partitions to partitions/FILE.csv, one per line. FILE is determined by the other options.")
    out_mode.add_argument('-F', '--form', action='store_true',
                      help="Output FORM representations of the partitions to partitions/FILE.hf. FILE is determined by the other options.")
    out_mode.add_argument('-r', '--reverse', action='store_true',
                        help="Reverse the order of integers in the partitions.")
    out_mode.add_argument('-R', '--reverse-output', action='store_true',
                        help="Reverse the order in which partitions are output.")


    parser.add_argument('-v', '--verbose', action='store_true',
                      help="Print more information about what is done. Implies --std.")

    parser.add_argument('integer', type=int, metavar='INT',
                      help="The integer to be partitioned.")

    args = parser.parse_args()

    # Combine options
    write_file = any((args.csv, args.txt, args.form))
    write_std = args.std or not write_file

    # Get modifiers
    filters = []
    if args.even:
        filters.append("(x % 2) == 0")
    elif args.odd:
        filters.append("(x % 2) != 0")
    if args.min:
        filters.append(f"x >= {args.min[0]}")
    if args.max:
        filters.append(f"x <= {args.max[0]}")
    filter = eval("lambda x:" + (' and '.join(filters) if filters else 'True'))

    # Select mode and compute partition
    if args.unordered:
        name = "Unordered"
        tag = 'u'
    else:
        name = "Ordered"
        tag = 'o'
    if args.fixed:
        name += f" length-{args.fixed[0]}"
        tag += f'f{args.fixed[0]}'
        parts = ufpart(args.integer, args.fixed[0], filter) if args.unordered else ofpart(args.integer, args.fixed[0], filter)
    else:
        parts = upart(args.integer, filter) if args.unordered else opart(args.integer, filter)

    # Setup output
    if write_file:
        makedirs('partitions', exist_ok=True)
    if args.reverse:
        tag += 'r'
    if args.reverse_output:
        tag += 'R'
    filename = f"partitions/{args.integer}{tag}"
    def rev(arr, rev):
        yield from reversed(arr) if rev else arr

    # Do output
    if args.verbose:
        print(f"{name} partitions of {args.integer}:")
    with (CondIO(enable_std = (write_std or args.verbose))
          .add(args.txt, f"{filename}.txt", 'w', 'txt')
          .add(args.csv, f"{filename}.csv", 'w', 'csv')
          .add(args.form, f"{filename}.hf", 'w', 'hf')
          ) as out:

        out.print(f"* Generated by ipart ({__file__}) with options {' '.join(argv)} on {datetime.now().strftime('%c')}", 'hf')
        for part in rev(parts, args.reverse_output):
            out.print(' '.join(str(p) for p in rev(part, args.reverse)))
            out.print(' '.join(str(p) for p in rev(part, args.reverse)), 'txt')
            out.print(','.join(str(p) for p in rev(part, args.reverse)), 'csv')
            out.print(f"   + ipart({','.join(str(p) for p in rev(part, args.reverse))})", 'hf')

    if args.verbose:
        for ext in ('txt', 'csv', 'hf'):
            if out.is_enabled(ext):
                print(f"Wrote to {filename}.{ext}")

if __name__ == '__main__':
    main(argv[1:])

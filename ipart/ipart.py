#!/bin/python3
# By Mattias Sjö, 2024
#
# Computes integer partitions
# Run with argument --help for more instructions
#
# Generates the partitions in lexicographic order using a straightforward recursive algorithm with caching.
# Prints them to the screen and prepares a form file called ipart/(concatenation of arguments).hf

import argparse
from datetime import datetime
from functools import cache
from os import makedirs
from sys import argv


# These three implemetations are very similar, but a bit of code repitition is clearer
# than the various conditionals needed to fit all in one function

@cache
def _upart(tot):
    if tot <= 0:
        return [[]]
    heads = [n+1 for n in range(tot)]
    return [[head] + tail
                for head in reversed(heads)
                for tail in upart(tot-head)]

def upart(integer):
    """
    Compute an unordered integer partition.

    Arguments:
    integer -- the nonnegative integer to be partitioned

    Returns:
    A list containing all lists of positive integers such that sum(list) = integer
    They are ordered lexicographically; thus, the first one is [tot] and the last is [1]*tot.
    If integer is 0, then the result is [].
    """
    if integer < 0:
        raise ValueError(f"Integer must be non-negative ({integer} provided)")
    return _upart(integer)


@cache
def _opart(tot, maxpart):
    if tot <= 0:
        return [[]]
    heads = [n+1 for n in range(min(maxpart,tot))]
    return [[head] + tail
                for head in reversed(heads)
                for tail in _opart(tot-head, head)]
def opart(integer):
    """
    Compute an ordered integer partition.

    Arguments:
    integer -- the nonnegative integer to be partitioned

    Returns:
    A list containing all (descendingly) sorted lists of positive integers such that sum(list) = integer.
    They are ordered lexicographically; thus, the first one is [integer] and the last is [1]*integer.
    If integer is 0, then the result is [].
    """
    if integer < 0:
        raise ValueError(f"Integer must be non-negative ({integer} provided)")
    return _opart(integer, integer)
    
@cache
def _fpart(tot, length):
    if length <= 0:
        return [[]]
    elif length == 1:
        return [[tot]]
    heads = [n for n in range(tot+1)]
    return [[head] + tail
                for head in reversed(heads)
                for tail in fpart(tot-head, length-1)]

def fpart(integer, length):
    """
    Compute a fixed-length unordered integer partition.

    Arguments:
    integer -- the nonnegative integer to be partitioned
    length -- the length of the partition

    Returns:
    A list containing all lists of nonnegative integers such that sum(list) = integer and len(list) = integer.
    They are ordered lexicographically; thus, the first one is [integer]+[0]*(length-1) and the last is the reverse of that.
    If integer is 0, then the result is [[0]].
    If length is 0, then the result is [].
    """
    if integer < 0:
        raise ValueError(f"Integer must be non-negative ({integer} provided)")
    if length < 0:
        raise ValueError(f"Length must be non-negative ({length} provided)")
    return _fpart(integer, length)


def main(argv):

    parser = argparse.ArgumentParser(
        prog='ipart',
        formatter_class=argparse.RawTextHelpFormatter,
        description="Utility for generating integer partitions.\nBy Mattias Sjö, 2024-25",
        epilog="The mode options -[ouf] are mutually exclusive.\nMore than one of the output options -[stcF] may be used simultaneously.\n \nThis uses a straightforward non-lazy recursive algorithm that, thanks to extensive caching, should be more-or-less linear in the number of partitions, which is in turn exponential in INT even in the --ordered case.")

    part_mode = parser.add_mutually_exclusive_group()
    part_mode.add_argument('-o', '--ordered', action='store_true',
                           help="Generate ordered partitions into positive integers. This is the default.")
    part_mode.add_argument('-u', '--unordered', action='store_true',
                           help="Generate unordered partititons into positive integers.")
    part_mode.add_argument('-f', '--fixed', action='store', nargs=1, type=int, metavar='N',
                           help="Generate unordered partitions into a fixed number N of non-negative integers.")

    parser.add_argument('-s', '--std', action='store_true',
                      help="Output whitespace-separated partitions to stdout, one per line. This is the default.")
    parser.add_argument('-t', '--txt', action='store_true',
                      help="Output whitespace-separated partitions to ipart/FILE.txt, one per line. FILE is determined by the other options.")
    parser.add_argument('-c', '--csv', action='store_true',
                      help="Output comma-separated partitions to ipart/FILE.csv, one per line. FILE is determined by the other options.")
    parser.add_argument('-F', '--form', action='store_true',
                      help="Output FORM representations of the partitions to ipart/FILE.hf. FILE is determined by the other options.")

    parser.add_argument('-v', '--verbose', action='store_true',
                      help="Implies --std, and prints more information about what is done.")

    parser.add_argument('integer', type=int, metavar='INT',
                      help="The integer to be partitioned.")

    args = parser.parse_args()

    write_file = any((args.csv, args.txt, args.form))
    write_std = args.std or not write_file

    if args.unordered:
        name = "Unrdered"
        tag = 'u'
        parts = upart(args.integer)
    elif args.fixed:
        name = f"Length-{args.fixed[0]}"
        tag = f'f{args.fixed[0]}'
        parts = fpart(args.integer, args.fixed[0])
    else:
        name = "Ordered"
        tag = 'o'
        parts = opart(args.integer)

    if write_file:
        makedirs('ipart', exist_ok=True)
        filename = f"ipart/{args.integer}{tag}"

    if args.verbose:
        print(f"{name} partitions of {args.integer}:")
    if write_std or args.verbose:
        for part in parts:
            print(' '.join(str(p) for p in part))
    if args.txt:
        with open(f"{filename}.txt", 'w') as out:
            for part in parts:
                print(' '.join(str(p) for p in part), file=out)
        if args.verbose:
            print(f"Wrote to {filename}.txt")
    if args.csv:
        with open(f"{filename}.csv", 'w') as out:
            for part in parts:
                print(','.join(str(p) for p in part), file=out)
        if args.verbose:
            print(f"Wrote to {filename}.csv")
    if args.form:
        with open(f"{filename}.hf", 'w') as out:
            print(f"* Generated by ipart ({__file__}) with options {' '.join(argv)} on {datetime.now().strftime('%c')}", file=out)
            for part in parts:
                print(f"   + ipart({','.join(str(p) for p in part)})", file=out)
        if args.verbose:
            print(f"Wrote to {filename}.hf")

if __name__ == '__main__':
    main(argv[1:])

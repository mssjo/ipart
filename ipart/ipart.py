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
    heads = [n+1 for n in range(tot) if filter(n+1)]
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
def _ufpart(tot, length, filter):
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

def main():

    # Parse arguments
    parser = argparse.ArgumentParser(
        prog='ipart',
        formatter_class=argparse.RawTextHelpFormatter,
        description="Utility for generating integer partitions.\nBy Mattias Sjö, 2025",
        epilog="This uses a straightforward non-lazy recursive algorithm that, thanks to extensive caching, should be more-or-less linear in the number of partitions, which, however, is in turn exponential in INTEGER.")


    parser.add_argument('integer', type=int, metavar='INTEGER',
                      help="The integer to be partitioned.")

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

    out_mode = parser.add_argument_group("output options",
                                         description="For each output mode provided, partitions are written to the given FILE (overwriting any previous contents), or to stdout if FILE is omitted. Multiple formats cannot be written to the same FILE (or stdout). If no output option is given, it defaults to -s.")

    STDOUT = None
    NOT_GIVEN = 0
    out_mode_fmt = {'action':'store', 'nargs':'?', 'type':str, 'metavar':'FILE', 'const':STDOUT, 'default':NOT_GIVEN}
    out_mode.add_argument('-s', '--spaces', **out_mode_fmt,
                      help="Output partitions as lines of numbers separated by spaces. This is the default.")
    out_mode.add_argument('-t', '--tabs', **out_mode_fmt,
                      help="Like -s, but use tabulators.")
    out_mode.add_argument('-c', '--commas', **out_mode_fmt,
                      help="Like -s, but use commas.")
    out_mode.add_argument('-p', '--paren-list', **out_mode_fmt,
                      help="Output partitions as a list of lists, using commas and parentheses.")
    out_mode.add_argument('-b', '--bracket-list', **out_mode_fmt,
                      help="Like -p but with square brackets, conforming with the syntax of e.g. Python.")
    out_mode.add_argument('-B', '--brace-list', **out_mode_fmt,
                      help="Like -b, but with curly braces, conforming with the syntax of e.g. C/C++ and Mathematica.")
    out_mode.add_argument('-F', '--form', **out_mode_fmt,
                      help="Output partitions using FORM syntax, as a sum where each term is the function \"ipart\" with the partition as arguments.")
    out_mode.add_argument('-w', '--wolfram', **out_mode_fmt,
                      help="Like -F, but using Mathematica syntax.")

    other = parser.add_argument_group("other options")
    other.add_argument('-H', '--header', action='store', nargs='?', const='', default=None, metavar='PREFIX',
                       help="Equip each output file (not stdout) with a header stating how and when it was generated, prefixed by PREFIX (default: nothing, unless the only output file is in form mode, in which case it is '*')")
    other.add_argument('-r', '--reverse', action='store_true',
                        help="Reverse the order of integers in the partitions.")
    other.add_argument('-R', '--reverse-output', action='store_true',
                        help="Reverse the order in which partitions are output.")
    other.add_argument('-v', '--verbose', action='store_true',
                      help="Print more information about what is done. Implies -s if nothing else is printed to stdout.")


    args = parser.parse_args()

    # Get modifiers
    filters = []
    description = ""
    if args.even:
        filters.append("(x % 2) == 0")
        description += "into even integers"
    elif args.odd:
        filters.append("(x % 2) != 0")
        description += "into odd integers"
    if args.min or args.max:
        if not description:
            description += "into integers"
        if args.min and args.max:
            description += f" between {args.min[0]} and {args.max[0]} (inclusive)"
        if args.min:
            filters.append(f"x >= {args.min[0]}")
            if not args.max:
                description += f" greater than {args.min[0]-1}"
        if args.max:
            filters.append(f"x <= {args.max[0]}")
            if not args.min:
                description += f" less than {args.max[0]+1}"
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
    def rev(arr, rev):
        yield from reversed(arr) if rev else arr

    out_modes = {
        'spaces' : (lambda part: ' ' .join(part), '', '', '\n'),
        'tabs'   : (lambda part: '\t'.join(part), '', '', '\n'),
        'commas' : (lambda part: ',' .join(part), '', '', '\n'),
        'form'   : (lambda part: f"   + ipart({','.join(part)})", '', '', '\n'),
        'wolfram': (lambda part: f"   + ipart[{','.join(part)}]", '(\n', '\n)', '\n'),
        'paren_list'   : (lambda part: f"    ({','.join(part)})", '(\n', '\n)', ',\n'),
        'bracket_list' : (lambda part: f"    [{','.join(part)}]", '[\n', '\n]', ',\n'),
        'brace_list'   : (lambda part: f"   {{{','.join(part)}}}", '{\n', '\n}', ',\n')}

    outputs = {}
    for mode,fmt in out_modes.items():
        target = vars(args)[mode]
        if target is NOT_GIVEN:
            continue
        elif target in outputs:
            raise argparse.ArgumentError(f"""More than one output targeting {f'"{target}"' if target != STDOUT else 'stdout'}""")
        outputs[target] = fmt

    # Special cases
    if not outputs or (args.verbose and (STDOUT not in outputs)):
        outputs[STDOUT] = out_modes['spaces']
    if args.form and sum(1 for target in outputs.keys() if target) and args.header == '':
        args.header = '* '

    out = CondIO(enable_std = (STDOUT in outputs))
    for target in outputs.keys():
        if target != STDOUT:
            out.add(True, target, 'w')

    # Do output
    if args.verbose:
        print(f"{name} partitions of {args.integer}{f' {description}:' if description else ':'}")
    with out:
        count = 0
        for target, (_, pre, _, _) in outputs.items():
            if target and args.header is not None:
                out.print(f"{args.header}Generated by ipart ({__file__}) with options {' '.join(argv[1:])} on {datetime.now().strftime('%c')}", target)
            out.print(pre, target, end='')
        for part in rev(parts, args.reverse_output):
            for target, (fmt, _, _, sep) in outputs.items():
                out.print((sep if count > 0 else '') + fmt(str(p) for p in rev(part, args.reverse)), target, end='')
            count += 1
        for target, (_, _, post, _) in outputs.items():
            out.print(post, target)

    if args.verbose:
        for target in outputs.keys():
            if target:
                print(f"Wrote to {target}")
        print(f"Generated {count} partition{'s' if count != 1 else ''}")

if __name__ == '__main__':
    main()

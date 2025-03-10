# ipart
Simple utility for generating integer partitions
By Mattias Sjö, 2024-25

## Installation

Make `ipart/ipart.py` executable and add it to your `$PATH`; optionally alias it to `ipart` for simplicity.
Use `pip` to install the python package `ipart` described by `setup.py`, then import it where you need with `import ipath`.

## Usage

Run `ipart.py --help` for usage of the command-line tool.

The python library provides the functions `opart`, `upart`, `ofpart` and `ufpart` which produce partitions with the corresponding combination of the `-[ouf]` flags of the command-line tool.
See the docstrings in `ipart/ipart.py` for details.

## Dependencies

My conditional IO library (https://github.com/mssjo/condIO)

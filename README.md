# ipart
Simple utility for generating integer partitions

Usage:
```
ipart [uo] NUMBER
ipart f NUMBER LENGTH
```
The first version generates `o`rdered or `u`nordered partitions of `NUMBER`, i.e. all (un)ordered sequences of positive numbers that add up to `NUMBER`.
The second version generates `f`ixed-length partitions, i.e. all sequences of length `LENGTH` of non-negative numbers that add up to `NUMBER`.

All versions use a straightforward algorithm that, thanks to extensive caching, should be more-or-less linear in the number of partitions, which is in turn exponential in `NUMBER` even in the ordered case.

Alternatively, the functions `opart(number)`, `upart(number)` and `fpart(number,length)` can be accessed as a python library via
```
import ipart
```

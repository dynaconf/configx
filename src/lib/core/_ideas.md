# Core Data Structure

see: https://wiki.python.org/moin/DictionaryKeys
see: https://python.land/python-data-types/dictionaries

tree libs:
https://github.com/c0fec0de/anytree
https://github.com/caesar0301/treelib

## Draft ideias

### Caching

> leaves caching

Instead of traversing the Tree each time for finding a giving
Setting, it could retrieve the settings from a cache, given
there where no modifications to the Tree (or the specific Setting)
and the environment did not change.

This cache would store the Setting path as hash-key,
so it's retrieved in O(1)

### Bucket Data Structure

operation:

- get Setting from all envs

# FstStr

FstStr is a small library providing a string-oriented Python interface to
OpenFST. It is build on the `pywrapfst` library that is distributed with
OpenFST.

## Usage

FstStr includes several types of functions that make working with strings in
OpenFST more comfortable. These include defining SymbolTables, applying FSTs to
strings, and several component steps.

### Working with symbols and SymbolTables

SymbolTables define a mapping between integer indices and the input/output
alphabet of an FST. An example alphabet for English (`EN_SYMB`) is included in fststr.

```
>>> from fststr import fststr
>>> fststr.EN_SYMB
['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i' 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', "'", "'", '+Known', '+Guess', '<other>', '<c>', '<v>']
```

To convert this alphabet to a symbol table, use `symbol_table_from_alphabet`:

```
>>> st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
```

This symbol table can then be passed to an FST compiler as the input/output
symbols tables for an FST.

### Compiling and manipulating FSTs
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

```python
>>> from fststr import fststr
>>> fststr.EN_SYMB
['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i' 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', "'", "'", '+Known', '+Guess', '<other>', '<c>', '<v>']
```

To convert this alphabet to a symbol table, use `symbol_table_from_alphabet`:

```python
>>> st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
```

This symbol table can then be passed to an FST compiler as the input/output
symbols tables for an FST.

### Compiling and manipulating FSTs

FstStr currently provides no abstraction over the process of defining and
compiling FSTs, but does provide some functions for maniuplating FSTs once they
are compiled.  To compile an FST, instantiate a compiler (using the symbol table
`st` for both input and output):

```python
>>> import pywrapfst as fst
>>> compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
```

The resulting object, `compiler` is a file-like object. You pass a transition
table to `compiler` by writing to it and compile the FST corresponding to the
transition table by calling the `compile` method:

```python
>>> print('0 1 a b\n1 2 b c\n2 3 c d\n3', file=compiler)
>>> abc2bcd = compiler.compile()
```
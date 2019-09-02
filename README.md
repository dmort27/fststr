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

Some shortcuts are often taken when defining FSTs. One is to use “other” as a
label on arcs, meaning that there is a transition with the label *x*:*x* for
every *x* not in the set of outgoing arcs from that state. This relieves the
author of the FST from the tedious and error-prone process of defining these
arcs manually. OpenFST does not support this notation directly, but `fststr`
provides a function that will take an FST including the symbol `<other>` and
mutate it so that the arcs with `<other>` are paralleled by the implied arc.
Consider the following example:

```python
>>> st = fststr.symbols_table_from_alphabet(alphabet)
>>> alphabet = ['A', 'a', 'b', 'c', '<other>']
>>> st = fststr.symbols_table_from_alphabet(alphabet)
>>> compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
>>> compiler.write('0 1 a A\n0 1 <other> <other>\n1\n')
>>> other = compiler.compile()
>>> print(other.__str__().decode('utf-8'))
0       1       a       A
0       1       <other> <other>
1
>>> fststr.expand_other_symbols(other)
>>> print(other.__str__().decode('utf-8'))
0       1       a       A
0       1       <other> <other>
0       1       A       A
0       1       b       b
0       1       c       c
1
```

Note that the arc labeled `<other>` will not be deleted, but this does not
matter as long as the input string does not contain the sequence "<other>".

Other, similar wildcard symbols can be defined and used following the example of
`<other>`.

### Application

Once you have an FST, you can apply it to a string. In reality, this is a four-step process:

1. Convert a string to a list of symbols and the list of symbols to a linear-chain automaton
2. Compose the FST from 2 with this automaton
3. Extract the unique paths through the resulting lattice
4. Convert these to strings

FstStr provides functions for doing each of these things and also provides a
single convenience function, `apply` that does all of them. This allows the
programmer to simply take a string, apply and FST to it, and get back the
resulting strings.

```python
>>> st = fststr.symbols_table_from_alphabet(['a', 'b', 'c', 'd', '<other>'])
>>> compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
>>> compiler.write('0 1 a <epsilon>\n0 1 <other> <other>\n1\n')
>>> del_a = compiler.compile()
>>> fststr.expand_other_symbols(del_a)
>>> fststr.apply('a', del_a)
['']
>>> fststr.apply('b', del_a)
['b']
>>> fststr.apply('c', del_a)
['c']
>>> fststr.apply('d', del_a)
['d']
```

### Example
Examples are in `examples/FSTs`. We will examine `e-insertion.txt. 
The FST takes in morphologically separated inputs like `fox<^>s<#>` and outputs 
`foxes<#>`.

Each line of the file represents information about the FST.

The first line `0` represents that q0 is a final state

The second line `0 0 <other> <other>` represents an arc from q0 to q0 with the value `<other> : <other>`

The fifth line `0 1 z z` represents an arc from q0 to q1 with the value `z : z`

See e-insertion.py for an example of how to run the FST.

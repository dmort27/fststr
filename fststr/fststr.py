 #!/usr/bin/env python3
"""FstrStrngr: A python module for operating on strings using OpenFST (pywrapfst)

This module provies a variety of different functions to make it easier to
process strings using OpenFST. OpenFST is powerful, but it is also very general,
and it is not immediately obvious how a user would use an FST compiled with
OpenFST to transduce strings. FstStr makes this easier by doing the tedious part
for you (so you can concentrate on building beautiful FSTs).

Generally, a workflow with FstStr is as follows:
1. Define a symbol set and generate a symbol table from it.
2. Compile one or more FSTs. Combine these FSTs via composition/union/concatentation/etc.
3. Apply the resulting transducer to strings
  (a) Convert a string to a list of symbols and the list of symbols to a linear-chain automaton
  (b) Compose the FST from 2 with this automaton
  (c) Extract the unique paths through the resulting lattice
  (d) Convert these to strings
With FstStr, Step 3 is wrapped up in a single convenience function, `apply`:

>>> fststr.apply('abc', capitalize)
['ABC']
"""

from collections import defaultdict
import pywrapfst as fst


class IllegalSymbol(Exception):
    pass


class FstError(Exception):
    pass

#############################################################################
# Managing symbol tables and symbol lists
#############################################################################

"""A list of symbols for English"""
EN_SYMB = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-''") + \
    ['+Known', '+Guess', '<other>', '<C>', '<V>', '<^>', '<#>']

def symbols_table_from_alphabet(alphabet):
    """Construct a SymbolTable from a list of strings.

    Args:
        alphabet: a list of strings to be treated as symbols

    Returns:
        SymbolTable: a symbol table with <epsilon> plus the symbols in strings.
    """
    st = fst.SymbolTable()
    st.add_symbol('<epsilon>', 0)
    for i, symb in enumerate(alphabet):
        st.add_symbol(symb, i+1)
    return st

def string_to_symbol_list(string, symbols):
    """Return a tokenization of a string into symbols

    Before a string can be converted to a linear-chain automaton, it must be
    decomposed into symbols. Some of these symbols may consist of a single
    character while others may consist of multiple characters.

    Args: string (str): the string to be tokenized sybmols (list): the symbols
        into which the string can be divided Returns: (list): a list of symbols
    """
    elements = []
    symbols = sorted(symbols, key=len, reverse=True)
    while string:
        matched = False
        for symbol in symbols:
            if symbol == string[0:len(symbol)]:
                elements.append(symbol)
                string = string[len(symbol):]
                matched = True
                break
        if not matched:
            raise IllegalSymbol('Substring "{}" starts with an unknown symbol'.format(string))
    return elements

#############################################################################
# Constructing FSTs
#############################################################################

def linear_fst(elements, automata_op, keep_isymbols=True, **kwargs):
    """Produce a linear automaton.

    Based on code from
    https://stackoverflow.com/questions/9390536/how-do-you-even-give-an-openfst-made-fst-input-where-does-the-output-go.

    Args: elements (list): ordered list of input symbols
        automata_op (Fst): automaton to apply
        keep_isymbols (bool): whether to keep the input symbols
    """

    st = isymbols=automata_op.input_symbols().copy()

    compiler = fst.Compiler(isymbols=st,
                            keep_isymbols=keep_isymbols,
                            acceptor=keep_isymbols,
                            **kwargs)
    
    for i, el in enumerate(elements):
        print('{} {} {}'.format(i, i+1, el), file=compiler)
    print(str(i+1), file=compiler)

    return compiler.compile()

#############################################################################
# Mutating FSTs
#############################################################################

def expand_other_symbols(automaton):
    """Adds arcs between states with an arc labeled <other>.

    If there is an arc a1 going from a state q1 to another state q2 and a1 has
    the ilabel <other>, this function will mutate the FST such that there are
    additional arcs between q1 and q2 with each label not represented among the
    out-going arcs from q1. This routine does not create arcs for special
    symbols wrapped in angle brakers (like <epsilon>, <^>, or <#>).

    Args: automaton (Fst): FST to be mutated
    """
    symbols = automaton.input_symbols().copy()
    symb_map = {symb: n for (n, symb) in symbols}
    other = symb_map['<other>']
    epsilon = symb_map['<epsilon>']
    special = {n for (symb, n) in symb_map.items() if symb[0] == '<' and symb[-1] == '>'}
    keys = {n for (n, _) in symbols} - special
    def dfs(start):
        visited, stack = set(), [start]
        while stack:
            state = stack.pop()
            if state not in visited:
                visited.add(state)
                arcs = {}
                for arc in automaton.arcs(state):
                    arcs[arc.ilabel] = {
                        'olabel': arc.olabel,
                        'nextstate': arc.nextstate
                    }
                stack.extend([arc.nextstate for arc in automaton.arcs(state)])
                if other in arcs:
                    nextstate = arcs[other]['nextstate']
                    for symb in keys - set(arcs):
                        olabel = arcs[other]['olabel']
                        olabel = symb if olabel == other else olabel
                        automaton.add_arc(
                                state,
                                fst.Arc(symb, olabel, 0.0, nextstate))
    dfs(automaton.start())
    return None

#############################################################################
# Operating on FSTs
#############################################################################

def apply_fst_to_list(elements, automaton, is_project=True, **kwargs):
    """Compose a linear automata generated from `elements` with `automata_op`.

    Based on code from
    https://stackoverflow.com/questions/9390536/how-do-you-even-give-an-openfst-made-fst-input-where-does-the-output-go.

    Args: elements (list): ordered list of edge symbols for a linear automata.
        automata_op (Fst): automata that will be applied.
        is_project (bool, optional): whether to keep only the output labels.
        kwargs: Additional arguments to the compiler of the linear automata .
    """
    linear_automata = linear_fst(elements, automaton, **kwargs)
    out = fst.compose(linear_automata, automaton)
    if is_project:
        out.project('output')
    return out

#############################################################################
# Extracting strings from FSTs
#############################################################################

def all_strings_from_chain(automaton):
    """Return all strings implied by a non-cyclic automaton

    Args:
        chain (Fst): a non-cyclic finite state automaton
    Returns:
        (list): a list of strings
    """
    def dfs(graph, path, paths=[]):
        target, label = path[-1]
        if graph.num_arcs(target):
            for arc in graph.arcs(target):
                new_target = arc.nextstate
                new_label = arc.olabel
                new_path = path + [(new_target, new_label)]
                paths = dfs(graph, new_path, paths)
        else:
            paths += [path]
        return paths
    if automaton.properties(fst.CYCLIC, True) == fst.CYCLIC:
        raise FstError('FSA resulting from composition of FST and linear chain automaton has cycles. Cannot extract set of strings.')
    start = automaton.start()
    paths = dfs(automaton, [(start, 0)])
    symb_tab = automaton.input_symbols().copy()
    strings = []
    for path in paths:
        strings.append(''.join([symb_tab.find(k) for (_, k) in path if k]))
    return strings

#############################################################################
# High-level convenience functions
#############################################################################

def apply(string, automaton):
    """Apply an FST to a string and get back the transduced strings

    Args:
        string (str): the string to which the FST is applied
        automaton: the FST applied to the string
    Returns:
        list: strings that result from the application of the FST to the string
    """
    symbols = [x for (_, x) in automaton.input_symbols()]
    elements = string_to_symbol_list(string, symbols)
    lattice = apply_fst_to_list(elements, automaton)
    if lattice.num_states() > 0:
        strings = all_strings_from_chain(lattice)
        return strings
    else:
        return []


def main():
    symbols = list('abcABC') + ['<other>']
    symb_tab = symbols_table_from_alphabet(symbols)
    # Construct compiler
    compiler = fst.Compiler(isymbols=symb_tab, osymbols=symb_tab, keep_isymbols=True, keep_osymbols=True)
    # Define transition table and print it to the compiler
    definition = \
"""0 1 <other> <other>
1 2 b B
1 0 <other> <epsilon>
0 2 a A
2
0
"""
    print(definition, file=compiler)
    # Compile the description, returning an Fst object
    scramble = compiler.compile()
    print('original fst')
    print(scramble.__str__())
    # Add transitions implied by <other>
    expand_other_symbols(scramble)
    print('expanded fst')
    print(scramble.__str__())
    # Apply the transducer to various inputs
    print('a -> ', apply('a', scramble)) # => ['A']
    print('bb -> ', apply('bb', scramble)) # => ['bB']
    print('bbcdefg -> ', apply('bb', scramble)) # => ['bB]
    print('cb -> ', apply('cb', scramble)) # => ['cB']
    print('ab -> ', apply('ab', scramble)) # => []
    print('aa -> ', apply('aa', scramble)) # => []
    
if __name__ == '__main__':
    main()

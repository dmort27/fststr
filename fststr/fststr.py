 #!/usr/bin/env python3
from collections import defaultdict

import pywrapfst as fst


class IllegalSymbol(Exception):
    pass


class FstError(Exception):
    pass

EN_SYMB = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-''") + \
    ['+Known', '+Guess']

def symbols_table_from_alphabet(alphabet):
    st = fst.SymbolTable()
    st.add_symbol('<epsilon>', 0)
    for i, symb in enumerate(alphabet):
        st.add_symbol(symb, i+1)
    return st


def linear_fst(elements, automata_op, keep_isymbols=True, **kwargs):
    """Produce a linear automata.

    Based on code from https://stackoverflow.com/questions/9390536/how-do-you-even-give-an-openfst-made-fst-input-where-does-the-output-go.

    Args:
        elements (list): ordered list of input symbols
        automata_op (Fst): automaton to apply
        keep_isymbols (bool): whether to keep the input symbols
    """
    compiler = fst.Compiler(isymbols=automata_op.input_symbols().copy(),
                            acceptor=keep_isymbols,
                            keep_isymbols=keep_isymbols,
                            **kwargs)

    for i, el in enumerate(elements):
        print("{} {} {}".format(i, i+1, el), file=compiler)
    print(str(i+1), file=compiler)

    return compiler.compile()


def apply_fst_to_list(elements, automata_op, is_project=True, **kwargs):
    """Compose a linear automata generated from `elements` with `automata_op`.

    Based on code from https://stackoverflow.com/questions/9390536/how-do-you-even-give-an-openfst-made-fst-input-where-does-the-output-go.

    Args:
        elements (list): ordered list of edge symbols for a linear automata.
        automata_op (Fst): automata that will be applied.
        is_project (bool, optional): whether to keep only the output labels.
        kwargs:
            Additional arguments to the compiler of the linear automata .
    """
    linear_automata = linear_fst(elements, automata_op, **kwargs)
    out = fst.compose(linear_automata, automata_op)
    if is_project:
        out.project(project_output=True)
    return out


def all_strings_from_chain(chain, symb_tab):
    """Return all strings implied by a non-cyclic automaton

    Args:
        chain (Fst): a non-cyclic finite state automaton
        symb_tab: the symbols table for chain
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
    if chain.properties(fst.CYCLIC, True) == fst.CYCLIC:
        raise FstError('FST is cyclic.')
    paths = dfs(chain, [(chain.start(), 0)])
    strings = []
    for path in paths:
        strings.append(''.join([symb_tab.find(k).decode('utf-8') for (_, k) in path if k]))
    return strings


def string_to_symbol_list(string, symbols):
    """Return a tokenization of a string into symbols

    Args:
        string (str): the string to be tokenized
        sybmols (list): the symbols into which the string can be divided
    Returns:
        (list): a list of symbols
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
            raise IllegalSymbol(f'Substring "{string}" starts with an unknown symbol')
    return elements


def apply(string, automata_op, symbols):
    elements = string_to_symbol_list(string, symbols)
    chain = apply_fst_to_list(elements, automata_op)
    strings = all_strings_from_chain(chain, symbols_table_from_alphabet(symbols))
    return strings


def main():
    symbols = list('ABCabc') + ['+Guess']
    symb_tab = symbols_table_from_alphabet(symbols)
    compiler = fst.Compiler(isymbols=symb_tab, osymbols=symb_tab, keep_isymbols=True, keep_osymbols=True)
    definition = """0 0 a A
0 0 a c
0 0 b b
0 1 b +Guess
0
1"""
    print(definition, file=compiler)
    caps_A = compiler.compile()
    print(apply('abab', caps_A, symbols))

if __name__ == '__main__':
    main()

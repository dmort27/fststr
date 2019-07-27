 #!/usr/bin/env python3
from collections import defaultdict

import pywrapfst as fst


class IllegalSymbol(Exception):
    pass


class FstError(Exception):
    pass

EN_SYMB = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-''") + \
    ['+Known', '+Guess', '<other>', '<c>', '<v>']

def symbols_table_from_alphabet(alphabet):
    st = fst.SymbolTable()
    st.add_symbol('<epsilon>', 0)
    for i, symb in enumerate(alphabet):
        st.add_symbol(symb, i+1)
    return st

def all_states(automaton):
    def dfs(graph, start):
        visited, stack = set(), [start]
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                visited.add(vertex)
                for arc in graph.arcs(vertex):
                    stack.append(arc.nextstate)
        return visited
    return dfs(automaton, 0)

def expand_other_symbols(automaton):
    symbols = automaton.input_symbols().copy()
    symb_map = {symb.decode('utf-8'): n for (n, symb) in symbols}
    other = symb_map['<other>']
    epsilon = symb_map['<epsilon>']
    keys = {n for (n, _) in symbols} - {other, epsilon}
    def dfs(start):
        visited, stack = set(), [start]
        while stack:
            state = stack.pop()
            if state not in visited:
                visited.add(state)
                arcs = defaultdict(set)
                all_labels = set()
                for arc in automaton.arcs(state):
                    arcs[arc.nextstate].add(arc.ilabel)
                    all_labels.add(arc.ilabel)
                for nextstate, ilabels in arcs.items():
                    if other in ilabels:
                        for ilabel in (keys - all_labels - {other, epsilon}):
                            automaton.add_arc(
                                state,
                                fst.Arc(ilabel, ilabel, fst.Weight.One(automaton.weight_type()),
                                nextstate))
        return visited
    dfs(automaton.start())
    print(automaton.__str__().decode('utf-8'))
    return None

                


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


def apply_fst_to_list(elements, automaton, is_project=True, **kwargs):
    """Compose a linear automata generated from `elements` with `automata_op`.

    Based on code from https://stackoverflow.com/questions/9390536/how-do-you-even-give-an-openfst-made-fst-input-where-does-the-output-go.

    Args:
        elements (list): ordered list of edge symbols for a linear automata.
        automata_op (Fst): automata that will be applied.
        is_project (bool, optional): whether to keep only the output labels.
        kwargs:
            Additional arguments to the compiler of the linear automata .
    """
    linear_automata = linear_fst(elements, automaton, **kwargs)
    out = fst.compose(linear_automata, automaton)
    if is_project:
        out.project(project_output=True)
    return out


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
        raise FstError('FST is cyclic.')
    start = automaton.start()
    paths = dfs(automaton, [(start, 0)])
    symb_tab = automaton.input_symbols().copy()
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
            raise IllegalSymbol('Substring "{}" starts with an unknown symbol'.format(string))
    return elements


def apply(string, automaton):
    """Apply an FST to a string and get back the transduced strings

    Args:
        string (str): the string to which the FST is applied
        automaton: the FST applied to the string
    Returns:
        list: strings that result from the application of the FST to the string
    """
    symbols = [x.decode('utf-8') for (_, x) in automaton.input_symbols()]
    elements = string_to_symbol_list(string, symbols)
    lattice = apply_fst_to_list(elements, automaton)
    if lattice.start() > -1:
        strings = all_strings_from_chain(lattice)
        return strings
    else:
        return []


def main():
    symbols = EN_SYMB
    symb_tab = symbols_table_from_alphabet(symbols)
    compiler = fst.Compiler(isymbols=symb_tab, osymbols=symb_tab, keep_isymbols=True, keep_osymbols=True)
    definition = """0 1 <other> <other>
1 2 b B
0 2 a A
2"""
    print(definition, file=compiler)
    scramble = compiler.compile()
    expand_other_symbols(scramble)
    print('a -> ', apply('a', scramble))
    print('bb -> ', apply('bb', scramble))
    print('cb -> ', apply('cb', scramble))
    print('ab -> ', apply('ab', scramble))
    print('aa -> ', apply('aa', scramble))
    print('dd -> ', apply('dd', scramble))

if __name__ == '__main__':
    main()

 #!/usr/bin/env python3

from collections import defaultdict

import pywrapfst as fst


def symbols_table_from_alphabet(alphabet):
    st = fst.SymbolTable()
    st.add_symbol('<eps>', 0)
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

def apply_fst(elements, automata_op, is_project=True, **kwargs):
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

def chain_fst_to_dag(f):
    """Converts an acyclic FST to a DAG represented as a dict

    Args:
        f (Fst): an acyclic FST
    Returns:
        dict: a dictionary-representation of the same network
    """
    dag = defaultdict(list)
    for transition in f.__str__().decode('utf-8').split('\n'):
        try:
            source, target, _, upper = transition.split('\t')
            dag[source].append((target, upper))
        except:
            continue
    return dag

def all_strings_from_dag(dag):
    """Extracts all strings corresponding to paths in a DAG

    Args:
        dag (dict): a dictionary; values are (state, label) pairs
    Returns:
        list: strings corresponding to each path through the input DAG
    """
    def dfs(data, path, paths=[]):
        target, label = path[-1]
        if target in data:
            for (new_target, new_label) in data[target]:
                new_path = path + [(new_target, new_label)]
                paths = dfs(data, new_path, paths)
        else:
            paths += [path]
        return paths
    paths = dfs(dag, [('0', '')])
    strings = []
    for path in paths:
        strings.append(''.join([l for (_, l) in path]))
    return strings

def main():
    f_ST = symbols_table_from_alphabet('ABCabc')
    compiler = fst.Compiler(isymbols=f_ST, osymbols=f_ST, keep_isymbols=True, keep_osymbols=True)
    definition = """0 0 a A
0 0 a c
0 0 b b
0"""
    print(definition, file=compiler)
    caps_A = compiler.compile()
    out = apply_fst(list('abab'), caps_A)
    dag = chain_fst_to_dag(out)
    print(dag)
    print(all_strings_from_dag(dag))


if __name__ == '__main__':
    main()

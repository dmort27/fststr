from fststr import fststr
import pywrapfst as fst

# Init FST
st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
fst_file = open('e-insertion.txt').read()
print(fst_file, file=compiler)
c = compiler.compile()
fststr.expand_other_symbols(c)

# Test FST
test_in = 'fox<^>s<#>'
print("input:", test_in)
print("output:", fststr.apply(test_in, c))

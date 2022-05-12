from cli.formatters import OutputFmt

csv_fmt = OutputFmt.CSV.get_formatter()


def test_csv_non_uniform_dicts():
    assert csv_fmt([{'a': 0, 'b': 1}, {'b': 2, 'c': 3}]) == """"a","b","c"\r
0,1,"<null>"\r
"<null>",2,3\r
"""


def test_csv_sorted_keys():
    assert csv_fmt({'d': 2, 'b': 0, 'a': 1, 'c': 3}) == """"a","b","c","d"\r
1,0,3,2\r
"""


def test_csv_flatten():
    assert csv_fmt({'a': {'b': {'c': 1}}, 'd': {'e': [1, 2, 3]}, 'f': 'foo'}) == """"a.b.c","d.e","f"\r
1,"[1, 2, 3]","foo"\r
"""


def test_csv_flatten_non_uniform():
    assert csv_fmt([{'a': {'b': 0}, 'c': 1}, {'a': {'b': 2, 'f': 4}, 'c': 3}]) == """"a.b","a.f","c"\r
0,"<null>",1\r
2,4,3\r
"""

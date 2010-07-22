from pymills.utils import notags

def test_notags():
    s = "<html>foo</html>"
    x = notags(s)
    assert x == "foo"

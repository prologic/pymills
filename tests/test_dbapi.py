
from pymills.dbapi import Connection

def test_sqlite():
    db = Connection("sqlite", ":memory:")

    rows = db.do("CREATE TABLE foo (x, y)")
    assert list(rows) == []

    rows = db.do("INSERT INTO foo VALUES (?, ?)", 1, 2)
    assert list(rows) == []

    rows = db.do("INSERT INTO foo VALUES (?, ?)", 3, 4)
    assert list(rows) == []

    rows = db.do("SELECT x, y FROM foo")
    rows = list(rows)
    assert len(rows) == 2

    assert rows[0].keys() == ["x", "y"]
    assert rows[0].items() == [("x", 1), ("y", 2)]
    assert rows[0].values() == [1, 2]

    assert rows[1].x == 3
    assert rows[1].y == 4

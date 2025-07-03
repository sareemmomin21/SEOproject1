import pytest
import psycopg2.extras
import src.database.database as db

class DummyCursor:
    def __init__(self):
        self.queries = []
        self._next_id = 123

    def execute(self, sql, params):
        self.queries.append((sql, params))

    def fetchone(self):
        return (self._next_id,)

    def close(self):
        pass

class DummyConn:
    def __init__(self):
        self.cur = DummyCursor()

    def cursor(self):
        return self.cur

    def commit(self):
        pass

    def close(self):
        pass

@pytest.fixture(autouse=True)
def patch_connect(monkeypatch):
    # every call to connect_db() returns our dummy connection
    monkeypatch.setattr(db, "connect_db", lambda: DummyConn())

def test_insert_scan_returns_id():
    scan_id = db.insert_scan("barcode", "123", ["vegan"], ["nuts"], 5.99)
    assert scan_id == 123

def test_insert_scan_sql_correct():
    conn = db.connect_db()
    _ = db.insert_scan("img", "/path/to/image", [], [], None)
    sql, params = conn.cur.queries[0]
    assert "INSERT INTO scans" in sql
    # match the parameters tuple
    assert params == ("img", "/path/to/image", [], [], None)

def test_insert_alternative_sql_correct():
    conn = db.connect_db()
    db.insert_alternative(7, "AltProd", {"cal":100}, 3.50, "Nice tip", "thumbs_up")
    sql, params = conn.cur.queries[0]
    assert "INSERT INTO alternatives" in sql
    # first two parameters should match what we passed
    assert params[0] == 7
    assert params[1] == "AltProd"
    # the JSON param should be wrapped in psycopg2.extras.Json
    assert isinstance(params[2], psycopg2.extras.Json)
    assert params[3] == 3.50
    assert params[4] == "Nice tip"
    assert params[5] == "thumbs_up"

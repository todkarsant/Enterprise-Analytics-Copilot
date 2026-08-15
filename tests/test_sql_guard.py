from app.services.sql_guard import validate_sql

def test_accepts_select():
    ok, reason, sql = validate_sql("SELECT store_id, SUM(sales) AS total_sales FROM store_week GROUP BY store_id")
    assert ok and sql

def test_rejects_mutation():
    ok, _, _ = validate_sql("DELETE FROM store_week")
    assert not ok

def test_rejects_unknown_column():
    ok, reason, _ = validate_sql("SELECT secret_column FROM store_week")
    assert not ok
    assert "Unknown column" in reason

def test_rejects_multiple_statements():
    ok, _, _ = validate_sql("SELECT * FROM store_week; DROP TABLE store_week")
    assert not ok

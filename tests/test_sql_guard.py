from app.services.sql_guard import validate_sql


def test_valid_select():
    valid, reason, normalized = validate_sql(
        "SELECT store_id, SUM(sales) AS total_sales "
        "FROM store_week GROUP BY store_id ORDER BY total_sales DESC LIMIT 10"
    )
    assert valid is True
    assert "total_sales" in normalized


def test_select_alias_is_not_treated_as_physical_column():
    valid, reason, normalized = validate_sql(
        "SELECT region, SUM(sales) AS total_sales "
        "FROM store_week GROUP BY region ORDER BY total_sales DESC"
    )
    assert valid is True


def test_reject_unknown_column():
    valid, reason, normalized = validate_sql(
        "SELECT store_id, customer_lifetime_value FROM store_week"
    )
    assert valid is False
    assert "Unknown column" in reason


def test_reject_mutation():
    valid, reason, normalized = validate_sql(
        "DELETE FROM store_week"
    )
    assert valid is False


def test_reject_multiple_statements():
    valid, reason, normalized = validate_sql(
        "SELECT sales FROM store_week; DROP TABLE store_week"
    )
    assert valid is False


def test_valid_physical_table_alias():
    valid, reason, normalized = validate_sql(
        "SELECT sw.store_id, SUM(sw.sales) AS total_sales "
        "FROM store_week AS sw GROUP BY sw.store_id ORDER BY total_sales DESC"
    )
    assert valid is True


def test_reject_unnecessary_self_join():
    valid, reason, normalized = validate_sql(
        "SELECT t1.store_id, SUM(t2.sales) AS total_sales "
        "FROM store_week AS t1 JOIN store_week AS t2 ON t1.store_id = t2.store_id "
        "GROUP BY t1.store_id"
    )
    assert valid is False
    assert "self-join" in reason.lower()

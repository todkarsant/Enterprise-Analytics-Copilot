from app.services.schema_catalog import retrieve_schema

def test_schema_retrieval_returns_context():
    result=retrieve_schema("compare sales and advertising spend by region")
    assert result["table"] == "store_week"
    assert result["context"]
    assert result["items"]

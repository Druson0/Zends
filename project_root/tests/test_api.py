# tests/test_api.py
"""Basic tests for the FastAPI RAG endpoints.

These tests verify that the API starts, can return results for a query, and can
accept a file upload for ingestion. They use FastAPI's TestClient which does not
require a running server.
"""
import io
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)

def test_query_endpoint():
    response = client.get("/query", params={"q": "test query"})
    assert response.status_code == 200
    json_data = response.json()
    assert "query" in json_data and json_data["query"] == "test query"
    # Results may be empty if the index has no data yet, but the structure must exist.
    assert "results" in json_data
    assert isinstance(json_data["results"], list)

def test_ingest_endpoint():
    # Create a simple in‑memory text file.
    file_content = "Hello world. This is a test document."
    files = {"file": ("test.txt", io.BytesIO(file_content.encode()), "text/plain")}
    response = client.post("/ingest", files=files)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data.get("status") == "ingested"
    assert json_data.get("filename") == "test.txt"

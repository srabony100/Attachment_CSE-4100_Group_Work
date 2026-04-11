from __future__ import annotations

from typing import Any

import numpy as np
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_active_user
from app.api.routes.search import router as search_router
from app.schemas.search import SearchResultItem


class FakeUser:
    id = 1
    role = "user"
    status = "active"


class FakeEmbedder:
    def embed(self, text: str) -> np.ndarray:
        normalized = text.lower().strip()
        if "array" in normalized and "python" in normalized:
            return np.array([1.0, 0.0, 0.0], dtype=np.float32)
        if "sort" in normalized and "javascript" in normalized:
            return np.array([0.0, 1.0, 0.0], dtype=np.float32)
        if "read file" in normalized and "c++" in normalized:
            return np.array([0.0, 0.0, 1.0], dtype=np.float32)
        if "raise" in normalized:
            raise RuntimeError("upstream embedding failure")
        return np.array([0.2, 0.2, 0.2], dtype=np.float32)


class FakeVectorStore:
    is_ready = True

    def search(self, query_vector: np.ndarray, top_k: int, tags: list[str]) -> list[SearchResultItem]:
        if float(query_vector[0]) == 1.0:
            return [
                SearchResultItem(
                    record_id="py-1",
                    title="How to declare an array in Python",
                    answer_snippet="Use a list: numbers = [1, 2, 3]",
                    tags=["python", "arrays"],
                    similarity_score=0.94,
                )
            ]
        if float(query_vector[1]) == 1.0:
            return [
                SearchResultItem(
                    record_id="js-1",
                    title="How to sort a list in JavaScript",
                    answer_snippet="Use array.sort((a, b) => a - b)",
                    tags=["javascript", "array"],
                    similarity_score=0.92,
                )
            ]
        if float(query_vector[2]) == 1.0:
            return [
                SearchResultItem(
                    record_id="cpp-1",
                    title="How to read a file in C++",
                    answer_snippet="Use std::ifstream to open and read file contents.",
                    tags=["c++", "file-io"],
                    similarity_score=0.91,
                )
            ]
        return []


def create_test_client() -> TestClient:
    app = FastAPI()
    app.include_router(search_router)
    app.state.embedder = FakeEmbedder()
    app.state.vector_store = FakeVectorStore()
    app.dependency_overrides[get_current_active_user] = lambda: FakeUser()
    return TestClient(app)


def test_search_examples_return_relevant_matches() -> None:
    client = create_test_client()
    cases = [
        ("how to declare array in python", "python"),
        ("how to sort a list in javascript", "javascript"),
        ("how to read file in c++", "c++"),
    ]

    for query, keyword in cases:
        response = client.post("/search", json={"query": query, "top_k": 5})
        assert response.status_code == 200
        payload = response.json()
        assert payload["results"], f"Expected results for query: {query}"
        title = payload["results"][0]["title"].lower()
        assert keyword in title


def test_empty_input_validation_error() -> None:
    client = create_test_client()
    response = client.post("/search", json={"query": "", "top_k": 5})
    assert response.status_code == 422


def test_backend_failure_is_handled_gracefully() -> None:
    client = create_test_client()
    response = client.post("/search", json={"query": "raise upstream failure", "top_k": 5})
    assert response.status_code == 502
    assert "Search failed" in response.json()["detail"]


def test_result_shape_contains_expected_fields() -> None:
    client = create_test_client()
    response = client.post("/search", json={"query": "how to sort a list in javascript", "top_k": 3})
    assert response.status_code == 200
    result = response.json()["results"][0]
    assert set(result.keys()) == {
        "record_id",
        "title",
        "answer_snippet",
        "tags",
        "similarity_score",
    }

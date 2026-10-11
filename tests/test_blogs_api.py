from starlette.testclient import TestClient
from src.main import app


def test_endpoints():
    client = TestClient(app)
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    paths = schema.get("paths", {})
    blog_paths = [p for p in paths if "/blogs" in p]
    assert len(blog_paths) > 0
    create_paths = [p for p in blog_paths if "/create" in p]
    assert len(create_paths) > 0


if __name__ == "__main__":
    test_endpoints()

import httpx
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_endpoints():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # Check openapi schema
        resp = client.get("/openapi.json")
        if resp.status_code != 200:
            print(f"Failed to fetch openapi.json: {resp.status_code}")
            sys.exit(1)
        schema = resp.json()
        paths = schema.get("paths", {})
        print("Checking blog endpoints in OpenAPI schema:")
        blog_paths = [p for p in paths if "/blogs" in p]
        for p in blog_paths:
            methods = list(paths[p].keys())
            print(f"  {p} -> {methods}")
        
        # Verify required endpoints exist
        create_paths = [p for p in blog_paths if "/create" in p]
        print(f"Found {len(blog_paths)} blog path registrations, create paths: {create_paths}")

if __name__ == "__main__":
    test_endpoints()

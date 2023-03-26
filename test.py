import httpx
import os

from dotenv import load_dotenv
load_dotenv()

# Replace 'http://localhost:8000' with the URL where your app is running
base_url = "http://localhost:8000"

BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
assert BEARER_TOKEN is not None

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

def test_certify_file():
    # Prepare a sample text file for testing
    file_name = "sample.txt"
    with open(file_name, "w") as f:
        f.write("This is a sample document for testing")

    with open(file_name, "rb") as f:
        files = {"file": (file_name, f)}
        response = httpx.post(f"{base_url}/certify-file", headers=headers, files=files)

    print(response.status_code)
    print(response.text)
    print(response.json())

if __name__ == "__main__":
    test_certify_file()


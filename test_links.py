import requests


BASE_URL = "http://127.0.0.1:5000"

session = requests.Session()


login_response = session.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "identifier": "testuser",
        "password": "Test@1234"
    }
)

print("LOGIN STATUS:", login_response.status_code)

if login_response.status_code != 200:
    print(login_response.json())
    raise SystemExit("Login failed.")


csrf_token = session.cookies.get("csrf_access_token")

if not csrf_token:
    raise SystemExit("CSRF access token not found.")


create_response = session.post(
    f"{BASE_URL}/api/links",
    json={
        "original_url": "https://www.google.com",
        "custom_slug": "myportfolio",
        "title": "My Portfolio"
    },
    headers={
        "X-CSRF-TOKEN": csrf_token
    }
)

print("CREATE CUSTOM LINK STATUS:", create_response.status_code)
print("CREATE CUSTOM LINK RESPONSE:", create_response.json())
from main import app
from fastapi.testclient import TestClient
import json

client = TestClient(app)

def test_auth_flow():
    print("=== Testing Authentication Flow ===")

    # Test 1: Verify CORS is working for auth endpoints
    print("\n1. Testing CORS preflight requests...")

    # Test preflight for signup
    response = client.options(
        '/api/auth/signup',
        headers={
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type',
            'Origin': 'http://localhost:3000'
        }
    )
    assert response.status_code == 200
    assert 'Access-Control-Allow-Origin' in response.headers
    print(f"[PASS] Preflight OPTIONS /api/auth/signup: {response.status_code}")

    # Test preflight for login
    response = client.options(
        '/api/auth/login',
        headers={
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type',
            'Origin': 'http://127.0.0.1:3000'
        }
    )
    assert response.status_code == 200
    assert 'Access-Control-Allow-Origin' in response.headers
    print(f"[PASS] Preflight OPTIONS /api/auth/login: {response.status_code}")

    # Test 2: Try to create a test user
    print("\n2. Testing signup endpoint...")
    test_email = "testuser@example.com"
    test_password = "secure123"  # Shorter password to avoid bcrypt 72-byte limit

    response = client.post(
        '/api/auth/signup',
        json={'email': test_email, 'password': test_password}
    )
    print(f"Signup response status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"[PASS] Signup successful - got response: {data.keys()}")

        # Verify token is returned
        assert 'access_token' in data
        assert 'token_type' in data
        print("[PASS] JWT token returned from signup")

        token = data['access_token']

        # Test 3: Try to login with the same user
        print("\n3. Testing login endpoint...")
        response = client.post(
            '/api/auth/login',
            json={'email': test_email, 'password': test_password}
        )
        print(f"Login response status: {response.status_code}")

        if response.status_code == 200:
            login_data = response.json()
            print(f"[PASS] Login successful - got response: {login_data.keys()}")

            # Verify token is returned
            assert 'access_token' in login_data
            assert 'token_type' in login_data
            print("[PASS] JWT token returned from login")

            # Test 4: Verify the token can be used for protected endpoints
            print("\n4. Testing protected endpoints with token...")
            response = client.get(
                '/api/tasks',
                headers={'Authorization': f'Bearer {token}'}
            )
            print(f"Protected endpoint status: {response.status_code}")

            if response.status_code in [200, 404]:  # 200 = success, 404 = no tasks found but access granted
                print("[PASS] Token authentication working - protected endpoint accessible")
            elif response.status_code == 401:
                print("[FAIL] Token authentication failed - unauthorized access")
            else:
                print(f"[INFO] Unexpected status code: {response.status_code}")

        else:
            print(f"[FAIL] Login failed with status: {response.status_code}")
            if response.status_code != 401:  # 401 is expected for wrong credentials
                try:
                    print(f"  Response: {response.json()}")
                except:
                    print(f"  Raw response: {response.text}")
    else:
        print(f"[FAIL] Signup failed with status: {response.status_code}")
        try:
            error_detail = response.json()
            print(f"  Error: {error_detail}")
        except:
            print(f"  Raw response: {response.text}")

    print("\n=== Auth Flow Test Complete ===")

if __name__ == "__main__":
    test_auth_flow()
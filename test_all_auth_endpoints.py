from main import app
from fastapi.testclient import TestClient
import json
import uuid

client = TestClient(app)

def test_all_auth_endpoints():
    print("=== Testing All Auth Endpoints ===")

    # Generate unique email for this test run
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"

    # Test 1: Signup
    print(f"\n1. Testing signup endpoint with email: {unique_email}...")
    signup_response = client.post(
        '/api/auth/signup',
        json={'email': unique_email, 'password': 'secure123'}
    )
    print(f"Signup response status: {signup_response.status_code}")
    if signup_response.status_code == 200:
        signup_data = signup_response.json()
        print(f"[PASS] Signup successful - token keys: {signup_data.keys()}")
        assert 'access_token' in signup_data
        assert 'token_type' in signup_data
        token = signup_data['access_token']
        print("[PASS] JWT token returned from signup")
    else:
        print(f"[FAIL] Signup failed: {signup_response.json()}")
        return False

    # Get the token from successful signup for later use
    if signup_response.status_code == 200:
        signup_data = signup_response.json()
        token = signup_data['access_token']
    else:
        print(f"[FAIL] Signup failed: {signup_response.json()}")
        return False

    # Test 2: Login with same credentials (should work)
    print("\n2. Testing login endpoint...")
    login_response = client.post(
        '/api/auth/login',
        json={'email': unique_email, 'password': 'secure123'}
    )
    print(f"Login response status: {login_response.status_code}")
    if login_response.status_code == 200:
        login_data = login_response.json()
        print(f"[PASS] Login successful - token keys: {login_data.keys()}")
        assert 'access_token' in login_data
        assert 'token_type' in login_data
        print("[PASS] JWT token returned from login")
    else:
        print(f"[FAIL] Login failed: {login_response.json()}")
        return False

    # Test 3: Login with wrong credentials (should fail)
    print("\n3. Testing login with wrong credentials...")
    wrong_login_response = client.post(
        '/api/auth/login',
        json={'email': unique_email, 'password': 'wrongpassword'}
    )
    print(f"Wrong login response status: {wrong_login_response.status_code}")
    if wrong_login_response.status_code == 401:
        print("[PASS] Login correctly failed with wrong credentials")
    else:
        print(f"[FAIL] Login should have failed with 401, got {wrong_login_response.status_code}")
        return False

    # Test 4: Try to signup with same email again (should fail)
    print("\n4. Testing duplicate signup...")
    dup_signup_response = client.post(
        '/api/auth/signup',
        json={'email': unique_email, 'password': 'anotherpassword'}
    )
    print(f"Duplicate signup response status: {dup_signup_response.status_code}")
    if dup_signup_response.status_code == 400:
        print("[PASS] Duplicate signup correctly failed with 400")
    else:
        print(f"[FAIL] Duplicate signup should have failed with 400, got {dup_signup_response.status_code}")
        return False

    # Test 5: Logout (currently just returns success message)
    print("\n5. Testing logout endpoint...")
    logout_response = client.post('/api/auth/logout')
    print(f"Logout response status: {logout_response.status_code}")
    if logout_response.status_code == 200:
        logout_data = logout_response.json()
        print(f"[PASS] Logout successful: {logout_data}")
    else:
        print(f"[FAIL] Logout failed: {logout_response.json()}")
        return False

    # Test 6: Test protected endpoints with token
    print("\n6. Testing protected endpoints with token...")
    protected_response = client.get(
        '/api/tasks',
        headers={'Authorization': f'Bearer {token}'}
    )
    print(f"Protected endpoint status: {protected_response.status_code}")
    # Status 200 or 404 are both acceptable (200 = success, 404 = no tasks found but access granted)
    if protected_response.status_code in [200, 404]:
        print("[PASS] Token authentication working - protected endpoint accessible")
    else:
        print(f"[FAIL] Token authentication failed - got {protected_response.status_code}")
        return False

    print("\n=== All Auth Endpoint Tests Passed! ===")
    return True

if __name__ == "__main__":
    success = test_all_auth_endpoints()
    if success:
        print("\nALL AUTH ENDPOINTS ARE FUNCTIONAL!")
    else:
        print("\nSOME TESTS FAILED!")
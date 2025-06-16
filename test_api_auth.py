import requests
import json

BASE_URL = "http://localhost:5000/api/auth"

def test_register():
    """Test user registration"""
    print("\n--- Testing Registration ---")
    
    # Test data
    data = {
        "username": "testuser",
        "password": "testpassword"
    }

    response = requests.post(f"{BASE_URL}/register", json=data)
    
    # Print results
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=4)}")
    
    return response.json() if response.status_code == 201 else None

def test_login(username="testuser", password="testpassword"):
    """Test user login"""
    print("\n--- Testing Login ---")

    data = {
        "username": username,
        "password": password
    }
    
    # Send request
    response = requests.post(f"{BASE_URL}/login", json=data)
    
    # Print results
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=4)}")
    
    return response.json() if response.status_code == 200 else None

def test_protected_endpoint(access_token):
    """Test protected endpoint access"""
    print("\n--- Testing Protected Endpoint ---")
    
    # Set authorization header
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Send request
    response = requests.get(f"{BASE_URL}/protected", headers=headers)
    
    # Print results
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=4) if response.status_code == 200 else response.text}")

def test_refresh_token(refresh_token):
    """Test token refresh"""
    print("\n--- Testing Token Refresh ---")
    
    # Set authorization header
    headers = {
        "Authorization": f"Bearer {refresh_token}"
    }
    
    # Send request
    response = requests.post(f"{BASE_URL}/refresh", headers=headers)
    
    # Print results
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=4) if response.status_code == 200 else response.text}")
    
    return response.json()["access_token"] if response.status_code == 200 else None

def run_tests():
    """Run all tests in sequence"""
    register_result = test_register()
    login_result = test_login()
    
    if login_result:
        test_protected_endpoint(login_result["access_token"])

        new_access_token = test_refresh_token(login_result["refresh_token"])
        
        if new_access_token:
            # Test protected endpoint with new access token
            print("\n--- Testing Protected Endpoint with Refreshed Token ---")
            test_protected_endpoint(new_access_token)

if __name__ == "__main__":
    run_tests()
    print("\nAPI Authentication Tests Completed")
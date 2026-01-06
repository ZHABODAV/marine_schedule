import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_endpoint(name, url, method='GET', data=None):
    print(f"Testing {name} ({method} {url})...")
    try:
        headers = {"Authorization": "Bearer test_token"}
        if method == 'GET':
            response = requests.get(f"{BASE_URL}{url}")
        else:
            response = requests.post(f"{BASE_URL}{url}", json=data, headers=headers)
        
        if response.status_code == 200:
            print(f"  [PASS] Status 200")
            try:
                json_data = response.json()
                keys = list(json_data.keys())
                print(f"  [INFO] Keys: {keys}")
                if 'vessels' in json_data:
                    print(f"  [INFO] Vessels count: {len(json_data['vessels'])}")
                if 'cargo' in json_data:
                    print(f"  [INFO] Cargo count: {len(json_data['cargo'])}")
                if 'templates' in json_data:
                    print(f"  [INFO] Templates count: {len(json_data['templates'])}")
                return True
            except:
                print(f"  [FAIL] Invalid JSON")
                return False
        else:
            print(f"  [FAIL] Status {response.status_code}")
            print(f"  [INFO] Response: {response.text}")
            return False
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        return False

def main():
    success = True
    success &= test_endpoint("Vessels", "/api/vessels")
    success &= test_endpoint("Cargo", "/api/cargo")
    success &= test_endpoint("Templates", "/api/voyage-templates")
    
    # Test Template Saving (requires auth usually, but let's try)
    # Note: require_auth decorator might block this if not authenticated.
    # But for now let's check if the endpoint exists and responds (even 401 is better than 404).
    
    template_data = {
        "name": "Test Template",
        "description": "Automated Test",
        "category": "Test",
        "ports": ["Port A", "Port B"],
        "estimatedDays": 5,
        "legs": []
    }
    # We expect 401 Unauthorized if auth is enabled, or 200 if not configured/dev mode
    print(f"Testing Template Save (POST /api/voyage-templates)...")
    try:
        response = requests.post(f"{BASE_URL}/api/voyage-templates", json=template_data)
        print(f"  [INFO] Status: {response.status_code}")
        if response.status_code in [200, 401]:
            print("  [PASS] Endpoint exists")
        else:
            print("  [FAIL] Endpoint issue")
            success = False
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        success = False

    if success:
        print("\nAll critical endpoints verified.")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()

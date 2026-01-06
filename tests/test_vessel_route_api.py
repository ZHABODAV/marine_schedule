import requests
import json
import time

BASE_URL = 'http://localhost:5000/api'

def test_vessels():
    print("Testing Vessels API...")
    
    # 1. Create Vessel
    vessel_data = {
        'id': 'TEST_VESSEL_01',
        'name': 'Test Vessel',
        'class': 'Test Class',
        'dwt': 50000,
        'speed': 12.5
    }
    
    response = requests.post(f'{BASE_URL}/vessels', json=vessel_data)
    if response.status_code == 201:
        print("[OK] Create Vessel: Success")
    else:
        print(f"[FAIL] Create Vessel: Failed ({response.status_code}) - {response.text}")
        
    # 2. Get Vessels
    response = requests.get(f'{BASE_URL}/vessels')
    if response.status_code == 200:
        vessels = response.json().get('vessels', [])
        found = any(v['id'] == 'TEST_VESSEL_01' for v in vessels)
        if found:
            print("[OK] Get Vessels: Found created vessel")
        else:
            print("[FAIL] Get Vessels: Created vessel not found")
    else:
        print(f"[FAIL] Get Vessels: Failed ({response.status_code})")

    # 3. Update Vessel
    update_data = {'name': 'Updated Test Vessel'}
    response = requests.put(f'{BASE_URL}/vessels/TEST_VESSEL_01', json=update_data)
    if response.status_code == 200:
        print("[OK] Update Vessel: Success")
    else:
        print(f"[FAIL] Update Vessel: Failed ({response.status_code}) - {response.text}")

    # 4. Delete Vessel
    response = requests.delete(f'{BASE_URL}/vessels/TEST_VESSEL_01')
    if response.status_code == 200:
        print("[OK] Delete Vessel: Success")
    else:
        print(f"[FAIL] Delete Vessel: Failed ({response.status_code}) - {response.text}")

def test_routes():
    print("\nTesting Routes API...")
    
    # 1. Create Route
    route_data = {
        'from': 'TestPortA',
        'to': 'TestPortB',
        'canal': None
    }
    
    response = requests.post(f'{BASE_URL}/routes', json=route_data)
    if response.status_code == 201:
        print("[OK] Create Route: Success")
        route = response.json().get('route')
        print(f"  Created Route ID: {route.get('route_id')}")
    else:
        print(f"[FAIL] Create Route: Failed ({response.status_code}) - {response.text}")
        
    # 2. Get Routes
    response = requests.get(f'{BASE_URL}/routes')
    if response.status_code == 200:
        routes = response.json().get('routes', [])
        found = any(r['from'] == 'TestPortA' and r['to'] == 'TestPortB' for r in routes)
        if found:
            print("[OK] Get Routes: Found created route")
        else:
            print("[FAIL] Get Routes: Created route not found")
    else:
        print(f"[FAIL] Get Routes: Failed ({response.status_code})")

if __name__ == '__main__':
    try:
        test_vessels()
        test_routes()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is it running?")

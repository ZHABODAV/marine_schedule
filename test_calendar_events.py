"""
Test script for /api/calendar/events endpoint
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:5000"

def test_calendar_events():
    """Test the calendar events endpoint with various filters"""
    
    print("=" * 80)
    print("Testing /api/calendar/events endpoint")
    print("=" * 80)
    
    # Test 1: Get all events
    print("\n1. Get all events (no filters)")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/api/calendar/events")
        if response.status_code == 200:
            data = response.json()
            print(f" Success! Got {data['metadata']['returned']} events (total: {data['metadata']['total']})")
            print(f"  Modules: {json.dumps(data['metadata']['statistics']['by_module'], indent=2)}")
            print(f"  Statuses: {json.dumps(data['metadata']['statistics']['by_status'], indent=2)}")
            if data['events']:
                print(f"\n  Sample event:")
                print(f"  {json.dumps(data['events'][0], indent=4)}")
        else:
            print(f" Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f" Exception: {e}")
    
    # Test 2: Filter by module (olya)
    print("\n\n2. Filter by module: olya")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/api/calendar/events?module=olya")
        if response.status_code == 200:
            data = response.json()
            print(f" Success! Got {data['metadata']['returned']} Olya events")
            if data['events']:
                print(f"  First event: {data['events'][0]['title']}")
        else:
            print(f" Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f" Exception: {e}")
    
    # Test 3: Filter by module (balakovo)
    print("\n\n3. Filter by module: balakovo")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/api/calendar/events?module=balakovo")
        if response.status_code == 200:
            data = response.json()
            print(f" Success! Got {data['metadata']['returned']} Balakovo events")
            if data['events']:
                print(f"  First event: {data['events'][0]['title']}")
        else:
            print(f" Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f" Exception: {e}")
    
    # Test 4: Filter by module (deepsea)
    print("\n\n4. Filter by module: deepsea")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/api/calendar/events?module=deepsea")
        if response.status_code == 200:
            data = response.json()
            print(f" Success! Got {data['metadata']['returned']} DeepSea events")
            if data['events']:
                print(f"  First event: {data['events'][0]['title']}")
        else:
            print(f" Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f" Exception: {e}")
    
    # Test 5: Filter by status
    print("\n\n5. Filter by status: planned")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/api/calendar/events?status=planned")
        if response.status_code == 200:
            data = response.json()
            print(f" Success! Got {data['metadata']['returned']} planned events")
        else:
            print(f" Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f" Exception: {e}")
    
    # Test 6: Filter by date range
    print("\n\n6. Filter by date range (next 30 days)")
    print("-" * 80)
    try:
        start_date = datetime.now().isoformat()
        end_date = (datetime.now() + timedelta(days=30)).isoformat()
        response = requests.get(
            f"{BASE_URL}/api/calendar/events?start_date={start_date}&end_date={end_date}"
        )
        if response.status_code == 200:
            data = response.json()
            print(f" Success! Got {data['metadata']['returned']} events in next 30 days")
        else:
            print(f" Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f" Exception: {e}")
    
    # Test 7: Multiple filters
    print("\n\n7. Multiple filters (module=deepsea, limit=5)")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/api/calendar/events?module=deepsea&limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f" Success! Got {data['metadata']['returned']} events (limited to 5)")
            for i, event in enumerate(data['events'], 1):
                print(f"  {i}. {event['title']} ({event['start']} to {event['end']})")
        else:
            print(f" Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f" Exception: {e}")
    
    # Test 8: Invalid module filter
    print("\n\n8. Test error handling (invalid module)")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/api/calendar/events?module=invalid")
        if response.status_code == 400:
            print(f" Correct error handling! Status: {response.status_code}")
            print(f"  Error message: {response.json().get('error', 'N/A')}")
        else:
            print(f" Unexpected status: {response.status_code}")
    except Exception as e:
        print(f" Exception: {e}")
    
    print("\n" + "=" * 80)
    print("Testing complete!")
    print("=" * 80)


if __name__ == "__main__":
    print("\nMake sure the API server is running on http://localhost:5000")
    print("You can start it with: python api_server.py\n")
    
    input("Press Enter to start testing...")
    test_calendar_events()

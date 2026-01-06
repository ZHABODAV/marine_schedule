#!/usr/bin/env python
"""
Automated UAT Test Script for Cargo Template API

Runs user acceptance tests and generates a report.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple


class CargoTemplateUATRunner:
    """Runs UAT tests for Cargo Template API."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.test_results: List[Tuple[str, bool, str]] = []
        self.created_templates: List[str] = []
    
    def login(self, username: str = "admin", password: str = "admin") -> bool:
        """Login and get authentication token."""
        print(" Logging in...")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                print(f" Login successful")
                return True
            else:
                 print(f" Login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f" Login error: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def test_create_template(self) -> bool:
        """Test Case 1: Create Cargo Template."""
        print("\n Test 1: Create Cargo Template")
        
        template_data = {
            "name": f"UAT Test Template {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "UAT test template",
            "commodity": "Iron Ore",
            "quantity": 75000,
            "loadPort": "Port Hedland",
            "dischPort": "Qingdao",
            "freightRate": 15.5,
            "operationalCost": 50000,
            "overheadCost": 10000,
            "otherCost": 5000,
            "isDefault": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/cargo-templates",
                json=template_data,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                self.created_templates.append(data["id"])
                print(f" Template created: {data['id']}")
                self.test_results.append(("Create Template", True, f"ID: {data['id']}"))
                return True
            else:
                print(f" Failed: {response.status_code} - {response.text}")
                self.test_results.append(("Create Template", False, f"Status: {response.status_code}"))
                return False
        except Exception as e:
            print(f" Error: {e}")
            self.test_results.append(("Create Template", False, str(e)))
            return False
    
    def test_get_all_templates(self) -> bool:
        """Test Case 2: Get All Templates."""
        print("\n Test 2: Get All Templates")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/cargo-templates",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                print(f" Retrieved {count} templates")
                self.test_results.append(("Get All Templates", True, f"Count: {count}"))
                return True
            else:
                print(f" Failed: {response.status_code}")
                self.test_results.append(("Get All Templates", False, f"Status: {response.status_code}"))
                return False
        except Exception as e:
            print(f" Error: {e}")
            self.test_results.append(("Get All Templates", False, str(e)))
            return False
    
    def test_get_template_by_id(self) -> bool:
        """Test Case 3: Get Template by ID."""
        print("\n Test 3: Get Template by ID")
        
        if not self.created_templates:
            print(" Skipped: No templates created")
            self.test_results.append(("Get Template by ID", None, "Skipped"))
            return True
        
        template_id = self.created_templates[0]
        
        try:
            response = requests.get(
                f"{self.base_url}/api/cargo-templates/{template_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f" Retrieved template: {data['name']}")
                self.test_results.append(("Get Template by ID", True, f"Name: {data['name']}"))
                return True
            else:
                print(f" Failed: {response.status_code}")
                self.test_results.append(("Get Template by ID", False, f"Status: {response.status_code}"))
                return False
        except Exception as e:
            print(f" Error: {e}")
            self.test_results.append(("Get Template by ID", False, str(e)))
            return False
    
    def test_update_template(self) -> bool:
        """Test Case 4: Update Template."""
        print("\n Test 4: Update Template")
        
        if not self.created_templates:
            print(" Skipped: No templates created")
            self.test_results.append(("Update Template", None, "Skipped"))
            return True
        
        template_id = self.created_templates[0]
        update_data = {
            "name": f"Updated UAT Template",
            "quantity": 80000
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/api/cargo-templates/{template_id}",
                json=update_data,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f" Updated template: {data['name']}, quantity: {data['quantity']}")
                self.test_results.append(("Update Template", True, "Updated successfully"))
                return True
            else:
                print(f" Failed: {response.status_code}")
                self.test_results.append(("Update Template", False, f"Status: {response.status_code}"))
                return False
        except Exception as e:
            print(f" Error: {e}")
            self.test_results.append(("Update Template", False, str(e)))
            return False
    
    def test_apply_template(self) -> bool:
        """Test Case 5: Apply Template."""
        print("\n Test 5: Apply Template")
        
        if not self.created_templates:
            print(" Skipped: No templates created")
            self.test_results.append(("Apply Template", None, "Skipped"))
            return True
        
        template_id = self.created_templates[0]
        override_data = {
            "quantity": 70000,
            "loadPort": "Newcastle"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/cargo-templates/{template_id}/apply",
                json=override_data,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f" Applied template with overrides")
                print(f"   Quantity: {data.get('quantity')}, Load Port: {data.get('loadPort')}")
                self.test_results.append(("Apply Template", True, "Applied successfully"))
                return True
            else:
                print(f" Failed: {response.status_code}")
                self.test_results.append(("Apply Template", False, f"Status: {response.status_code}"))
                return False
        except Exception as e:
            print(f" Error: {e}")
            self.test_results.append(("Apply Template", False, str(e)))
            return False
    
    def test_delete_template(self) -> bool:
        """Test Case 6: Delete Template."""
        print("\n Test 6: Delete Template")
        
        if not self.created_templates:
            print(" Skipped: No templates created")
            self.test_results.append(("Delete Template", None, "Skipped"))
            return True
        
        template_id = self.created_templates.pop()
        
        try:
            response = requests.delete(
                f"{self.base_url}/api/cargo-templates/{template_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                print(f" Deleted template: {template_id}")
                self.test_results.append(("Delete Template", True, f"ID: {template_id}"))
                return True
            else:
                print(f" Failed: {response.status_code}")
                self.test_results.append(("Delete Template", False, f"Status: {response.status_code}"))
                return False
        except Exception as e:
            print(f" Error: {e}")
            self.test_results.append(("Delete Template", False, str(e)))
            return False
    
    def cleanup(self):
        """Clean up created test templates."""
        print("\n Cleaning up test templates...")
        for template_id in self.created_templates:
            try:
                requests.delete(
                    f"{self.base_url}/api/cargo-templates/{template_id}",
                    headers=self.get_headers(),
                    timeout=10
                )
                print(f"   Deleted: {template_id}")
            except:
                pass
    
    def generate_report(self):
        """Generate test report."""
        print("\n" + "="*60)
        print(" UAT TEST REPORT - Cargo Template API")
        print("="*60)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {self.base_url}")
        print("-"*60)
        
        passed = sum(1 for _, result, _ in self.test_results if result is True)
        failed = sum(1 for _, result, _ in self.test_results if result is False)
        skipped = sum(1 for _, result, _ in self.test_results if result is None)
        total = len(self.test_results)
        
        for test_name, result, details in self.test_results:
            status_icon = "" if result is True else ("" if result is False else "")
            status_text = "PASS" if result is True else ("FAIL" if result is False else "SKIP")
            print(f"{status_icon} {test_name:30} [{status_text:4}] {details}")
        
        print("-"*60)
        print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
        
        if failed == 0:
            print(" ALL TESTS PASSED")
            print("="*60)
            return 0
        else:
            print(" SOME TESTS FAILED")
            print("="*60)
            return 1
    
    def run_all(self) -> int:
        """Run all UAT tests."""
        print(" Starting Cargo Template API UAT")
        print("="*60)
        
        # Login first
        if not self.login():
            print(" Cannot proceed without authentication")
            return 1
        
        # Run tests
        self.test_create_template()
        self.test_get_all_templates()
        self.test_get_template_by_id()
        self.test_update_template()
        self.test_apply_template()
        self.test_delete_template()
        
        # Cleanup
        self.cleanup()
        
        # Generate report
        return self.generate_report()


def main():
    """Main entry point."""
    runner = CargoTemplateUATRunner()
    exit_code = runner.run_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

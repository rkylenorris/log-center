import os
import requests


class LogAdmin:
    def __init__(self, api_url: str = None):
        self.api_url = api_url or os.getenv("LOG_CENTER_API_URL", "http://localhost:8000")
        self.admin_api_key = os.getenv("LOG_CENTER_ADMIN_KEY")
        if not self.admin_api_key:
            raise ValueError("Admin API key not found in environment variables.")
    
    def add_approved_user(self, owner_email: str, owner_name: str = None):
        headers = {
            "x-admin-api-key": self.admin_api_key,
            "Content-Type": "application/json"
        }
        
        data = {"owner_email": owner_email, "owner_name": owner_name}
        
        try:
            response = requests.post(f"{self.api_url}/users/approve", headers=headers, json=data)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to add approved user: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
        
    
    def request_api_key(self, owner_email: str, owner_name: str = None):
        
        headers = {
            "x-admin-api-key": self.admin_api_key,
            "Content-Type": "application/json"
        }
        
        if not owner_name:
            data = {"owner_email": owner_email}
        else:
            data = {"owner_email": owner_email, "owner_name": owner_name}
        
        try:
            response = requests.post(f"{self.api_url}/keys/create", headers=headers, json=data)
            if response.status_code == 200:
                return response.json()["key"]
            else:
                raise Exception(f"Failed to obtain API key: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    def deactivate_api_key(self, key: str):
        headers = {
            "x-admin-api-key": self.admin_api_key,
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(f"{self.api_url}/keys/deactivate/{key}", headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to deactivate API key: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    def deactivate_user(self, owner_email: str, owner_name: str = None):
        headers = {
            "x-admin-api-key": self.admin_api_key,
            "Content-Type": "application/json"
        }
        
        data = {"owner_email": owner_email, "owner_name": owner_name}
        
        try:
            response = requests.post(f"{self.api_url}/users/deactivate", headers=headers, json=data)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to deactivate user: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    def deactivate_api_key_by_owner(self, owner_email: str):
        headers = {
            "x-admin-api-key": self.admin_api_key,
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(f"{self.api_url}/keys/deactivate/{owner_email}", headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to deactivate API keys for owner: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    
    def get_active_api_keys(self):
        headers = {
            "x-admin-api-key": self.admin_api_key,
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(f"{self.api_url}/keys/active", headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get active API keys: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    
    def get_active_api_keys_by_owner(self, owner_email: str):
        headers = {
            "x-admin-api-key": self.admin_api_key,
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(f"{self.api_url}/keys/active/{owner_email}", headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get active API keys: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
import requests
import datetime
import time
import os
from .models import LogLevel

class LogWriter:
    def __init__(self, api_url: str, api_key: str, log_file: str = "failed_logs.txt", max_retries: int = 3, retry_delay: float = 2.0):
        self.api_url = api_url.rstrip('/')  # Ensure no trailing slash
        self.api_key = api_key
        self.log_file = log_file
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def log(self, level: LogLevel, message: str, process_name: str):
        log_data = {
            "level": level.value,
            "message": message,
            "process_name": process_name,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(f"{self.api_url}/logs/", json=log_data, headers=self.headers)
                
                if response.status_code == 200:
                    self._flush_failed_logs()
                    return response.json()
                else:
                    print(f"Attempt {attempt + 1} failed: {response.status_code} {response.text}")
                    time.sleep(self.retry_delay)
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                time.sleep(self.retry_delay)
        
        self._write_to_file(log_data)
        raise Exception(f"Failed to log message after {self.max_retries} attempts. Logged to file instead.")
    
    def _write_to_file(self, log_data):
        with open(self.log_file, "a") as file:
            file.write("|".join([log_data["timestamp"], log_data["level"], log_data["process_name"], log_data["message"]]) + "\n")
        print("Log written to file due to API failure.")
    
    def _flush_failed_logs(self):
        if not os.path.exists(self.log_file):
            return
        
        with open(self.log_file, "r") as file:
            lines = file.readlines()
        
        with open(self.log_file, "w") as file:
            for line in lines:
                timestamp, level, process_name, message = line.strip().split("|")
                log_data = {
                    "level": level,
                    "message": message,
                    "process_name": process_name,
                    "timestamp": timestamp
                }
                try:
                    response = requests.post(f"{self.api_url}/logs/", json=log_data, headers=self.headers)
                    if response.status_code != 200:
                        file.write(line)  # Keep log if still failing
                    else:
                        print("Flushed a previously failed log to API.")
                except requests.exceptions.RequestException:
                    file.write(line)
                    print("Failed to flush log entry.")
    
    def request_api_key(self, admin_api_key: str, owner_email: str):
        headers = {
            "x-admin-api-key": admin_api_key,
            "Content-Type": "application/json"
        }
        data = {"owner_email": owner_email}
        try:
            response = requests.post(f"{self.api_url}/keys/", headers=headers, json=data)
            if response.status_code == 200:
                return response.json()["key"]
            else:
                raise Exception(f"Failed to obtain API key: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

# Example usage
if __name__ == "__main__":
    API_URL = "http://127.0.0.1:8000"
    API_KEY = "your-api-key"  # Replace with a valid API key
    ADMIN_API_KEY = "your-admin-api-key"  # Admin key to request API keys
    
    logger = LogWriter(API_URL, API_KEY)
    try:
        response = logger.log(LogLevel.INFO, "This is a test log from the module", "TestProcess")
        print("Log successful:", response)
    except Exception as e:
        print("Error:", e)
    
    try:
        new_api_key = logger.request_api_key(ADMIN_API_KEY)
        print("New API Key Generated:", new_api_key)
    except Exception as e:
        print("Failed to generate API key:", e)

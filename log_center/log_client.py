import requests
import datetime
import time
import os
from .models import LogLevel

from colorama import init, Fore, Style, Back

init(autoreset=True)

class LogWriter:
    def __init__(self, api_url: str, api_key: str, console_level: LogLevel = LogLevel.INFO, 
                 log_file: str = "failed_logs.txt", max_retries: int = 3, retry_delay: float = 2.0):
        self.api_url = api_url.rstrip('/')  # Ensure no trailing slash
        self.api_key = api_key
        self.console_level = console_level
        self.log_file = log_file
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.color_map = {
            "DEBUG": Fore.GREEN,
            "INFO": Fore.WHITE,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED
        }
        self.start_time = datetime.datetime.now()
    
    
    def print_header(self, process_name: str, include_start_time: bool = True):
        padding = 10
        
        heading = f"DATETIME | PROCESS NAME | LEVEL | MESSAGE"
        if include_start_time:
            heading = f"\nLogging Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} \n{'='*padding}" + heading
        else:
            heading = f"\n{'='*padding}" + heading + f"{'='*padding}"
        
        print(Back.LIGHTWHITE_EX + Fore.BLACK + heading + Style.RESET_ALL)
    
    def _log_to_console(self, date_time: datetime.datetime, process_name: str, level: LogLevel, message: str):
        color = self.color_map.get(level.name, Fore.GREEN)
        print(f"{color}{date_time.strftime("%Y-%m-%d %H:%M:%S")} | {process_name} | {level.value}: {message}{Style.RESET_ALL}")
    
    def _log(self, level: LogLevel, message: str, process_name: str):
        log_time = datetime.datetime.now()
        log_data = {
            "level": level.value,
            "message": message,
            "process_name": process_name,
            "timestamp": log_time.isoformat()
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(f"{self.api_url}/logs/", json=log_data, headers=self.headers)
                
                if response.status_code == 200:
                    self._flush_failed_logs()
                    return response.json()
                else:
                    print(f"Log attempt {attempt + 1} failed: {response.status_code} {response.text}")
                    time.sleep(self.retry_delay)
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                time.sleep(self.retry_delay)
        
        self._write_to_file(log_data)
        raise Exception(f"Failed to log message after {self.max_retries} attempts. Logged to file instead.")
    
    def log_debug(self, message: str, process_name: str):
        return self._log(LogLevel.DEBUG, message, process_name)
    
    def log_info(self, message: str, process_name: str):
        return self._log(LogLevel.INFO, message, process_name)
    
    def log_warning(self, message: str, process_name: str):
        return self._log(LogLevel.WARNING, message, process_name)
    
    def log_error(self, message: str, process_name: str):
        return self._log(LogLevel.ERROR, message, process_name)
    
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
    

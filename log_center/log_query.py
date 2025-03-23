import requests
from typing import List
from .models import LogLevel


class LogQuery:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
    
    def get_logs_by_level(self, level: LogLevel) -> List[dict]:
        url = f"{self.api_url}/logs/level/{level.value}"
        return self._get(url)
    
    def get_logs_by_process(self, process_name: str) -> List[dict]:
        url = f"{self.api_url}/logs/process/{process_name}"
        return self._get(url)
    
    def get_logs_by_process_and_level(self, process_name: str, level: LogLevel) -> List[dict]:
        url = f"{self.api_url}/logs/filter/{process_name}/level/{level.value}"
    
    def get_logs_by_message_keyword(self, keyword: str) -> List[dict]:
        url = f"{self.api_url}/logs/filter/messages/{keyword}"
        return self._get(url)
    
    def get_logs_by_process_and_msg_keyword(self, process_name: str, keyword: str) -> List[dict]:
        url = f"{self.api_url}/logs/filter/{process_name}/messages/{keyword}"
        return self._get(url)
    
    def get_recent_logs(self, limit: int = 10) -> List[dict]:
        url = f"{self.api_url}/logs/recent/{limit}"
        return self._get(url)
    
    def get_logs_by_date(self, date: str) -> List[dict]:
        url = f"{self.api_url}/logs/date/{date}"
        return self._get(url)
    
    def get_logs_by_date_range(self, start_date: str, end_date: str) -> List[dict]:
        url = f"{self.api_url}/logs/filter/date-range/{start_date}/{end_date}"
        return self._get(url)
    
    def _get(self, url: str):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve logs: {e}")
            return []
        
    
# Example usage
if __name__ == "__main__":
    log_query = LogQuery()
    errors = log_query.get_logs_by_level(LogLevel.ERROR)
    print(f"Found {len(errors)} error logs")
    
    process_logs = log_query.get_logs_by_process("MyProcess")
    print(f"Found {len(process_logs)} logs for MyProcess")
    
    keyword_logs = log_query.get_logs_by_message_keyword("failure")
    print(f"Found {len(keyword_logs)} logs containing 'failure'")
    
    recent_logs = log_query.get_recent_logs()
    print(f"Most recent logs: {recent_logs}")

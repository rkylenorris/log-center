# Log Center

**Log Center** is a flexible Python logging platform with a RESTful API built using FastAPI. It allows applications to push logs, query logs, and manage API keys for secure access.

---

## 🚀 Features

- ✅ Post logs with metadata (level, process name, message, timestamp)
- 🔐 API key authentication for secure log access
- 👤 Admin-only API key generation and deactivation
- 🔎 Flexible log filtering (by level, process name, keyword)
- 📦 Python client module (`LogWriter`) for easy integration
- 🧵 Local file fallback when logging fails
- 🔄 Auto-retry + log flush on recovery

---

## 📦 Installation

```bash
pip install -e .
```

---

## 🌍 Running the API

### 1. Environment Setup

Create a `.env` file:

```env
LOG_CENTER_HOST=127.0.0.1
LOG_CENTER_PORT=8000
LOG_CENTER_ADMIN_KEY=super-secret-admin-key
LOG_CENTER_DB_URL=sqlite:///./logs.db
```

### 2. Run with Uvicorn

```bash
uvicorn main:app --reload
```

---

## 🔐 API Key Management

### Create API Key (admin-only)

```http
POST /keys/
Headers:
  x-admin-api-key: your-admin-key
Body:
{
  "owner_email": "user@example.com"
}
```

### Deactivate by Key

```http
POST /keys/deactivate/{key}
```

### Deactivate All for Owner

```http
POST /keys/deactivate/by-owner/{owner_email}
```

---

## 📝 Logging Endpoints

All routes require a valid `x-api-key`.

### Submit a Log

```http
POST /logs/
Body:
{
  "level": "ERROR",
  "message": "Something went wrong",
  "process_name": "MyApp",
  "timestamp": "2025-03-22T12:00:00"
}
```

### Query Logs

- `GET /logs/`
- `GET /logs/{level}`
- `GET /logs/process/{process_name}`
- `GET /logs/filter/{process_name}/{level}`
- `GET /logs/filter/{process_name}/message/{keyword}`

---

## 🐍 Python Client Example

```python
from log_center import APILogger

logger = APILogger(api_url="http://127.0.0.1:8000", api_key="your-api-key")
logger.log("INFO", "Something happened", "DataProcessor")
```

Request a key:

```python
logger.request_api_key(admin_api_key="your-admin-key", owner_email="me@example.com")
```

---

## 📁 Project Structure

```
log_center/
├── api.py         # All API routes
├── log_client.py  # Python logger class
├── log_query.py   # Query helper
├── models.py      # DB schema and enums
main.py            # App entrypoint
```

---

## 📜 License

MIT License

from fastapi import FastAPI
from log_center.api import router
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access secure keys from environment
ADMIN_API_KEY = os.getenv("LOG_CENTER_ADMIN_KEY")
DEFAULT_USER_API_KEY = os.getenv("LOG_CENTER_USER_KEY")

app = FastAPI(title="Log Center API")

# Make keys available to the app if needed
app.state.ADMIN_API_KEY = ADMIN_API_KEY
app.state.DEFAULT_USER_API_KEY = DEFAULT_USER_API_KEY

app.include_router(router)

# Entry point for running with uvicorn
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("LOG_CENTER_HOST", "127.0.0.1")
    port = int(os.getenv("LOG_CENTER_PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)



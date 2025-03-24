#!/bin/bash

# Configuration
RETRIES=30
WAIT=2
DB_HOST="sqlserver"
DB_PORT=1433

echo "⏳ Waiting for SQL Server at $DB_HOST:$DB_PORT..."

for i in $(seq 1 $RETRIES); do
    nc -z $DB_HOST $DB_PORT && break
    echo "🔁 Attempt $i/$RETRIES: SQL Server not ready yet. Retrying in ${WAIT}s..."
    sleep $WAIT
done

if [ "$i" = "$RETRIES" ]; then
    echo "❌ Failed to connect to SQL Server after $RETRIES attempts."
    exit 1
fi

echo "✅ SQL Server is up. Proceeding..."

echo "🛠 Creating database (if needed)..."
python create_database.py

echo "🚀 Launching FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

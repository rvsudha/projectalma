#!/usr/bin/env sh
set -e

# Wait for the database to accept connections (compose healthcheck also gates this).
python - <<'PY'
import os, time, sys
from sqlalchemy import create_engine, text
from app.core.config import settings

url = settings.sync_database_url
for attempt in range(1, 31):
    try:
        create_engine(url, pool_pre_ping=True).connect().close()
        print("database is ready")
        break
    except Exception as exc:  # noqa: BLE001
        print(f"waiting for database ({attempt}/30): {exc.__class__.__name__}")
        time.sleep(2)
else:
    print("database never became ready", file=sys.stderr)
    sys.exit(1)
PY

echo "running migrations..."
alembic upgrade head

echo "seeding attorney account..."
python -m scripts.seed

exec "$@"

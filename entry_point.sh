#! /bin/bash
python -m androidmonitor_backend.background &
uvicorn --host 0.0.0.0 --port 80 --workers 8 --forwarded-allow-ips=* androidmonitor_backend.app:app
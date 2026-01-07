#!/usr/bin/env bash
set -e

# Go to repo root (where this script lives)
cd "$(dirname "$0")"

# Activate venv (Windows Git Bash uses venv/Scripts/activate)
if [ -f "venv/Scripts/activate" ]; then
  source "venv/Scripts/activate"
elif [ -f "venv/bin/activate" ]; then
  source "venv/bin/activate"
else
  echo "Virtual environment not found. Expected venv/ folder."
  exit 1
fi

pytest -q

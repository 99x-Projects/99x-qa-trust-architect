#!/bin/sh
# Runs hooks/qa_guard.py with the first working Python 3.8+ interpreter.
# If none is found the guards are inactive (the tool call proceeds) and a warning is printed.
DIR=$(cd "$(dirname "$0")" && pwd)
for PY in python3 python py; do
  if command -v "$PY" >/dev/null 2>&1 &&
     "$PY" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >/dev/null 2>&1; then
    exec "$PY" "$DIR/qa_guard.py" "$@"
  fi
done
echo "qa-trust-architect: Python 3.8+ not found - guard hooks are inactive" >&2
exit 0

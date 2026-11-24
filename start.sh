#!/bin/sh
set -eu

exec python -m waitress --host=0.0.0.0 --port="${PORT:-5000}" --call app:create_app

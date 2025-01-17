#!/bin/bash

set -euo pipefail

./manage.py check --deploy
./manage.py migrate
./manage.py ensure_admins
./manage.py collectstatic --no-input

exec "$@"

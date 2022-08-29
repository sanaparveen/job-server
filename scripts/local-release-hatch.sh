#!/bin/bash
set -eu -o pipefail

RELEASE_HATCH_REPO=${RELEASE_HATCH_REPO:-./release-hatch}
RELEASE_HATCH_URL=${RELEASE_HATCH_URL:-http://localhost:8001}
WORKSPACE_DIR=${WORKSPACE_DIR:-./workspaces}

mkdir -p "$WORKSPACE_DIR"

if test -d "$RELEASE_HATCH_REPO"; then
    git -C "$RELEASE_HATCH_REPO" pull
else
    git clone https://github.com/opensafely-core/release-hatch "$RELEASE_HATCH_REPO"
fi
env -C "$RELEASE_HATCH_REPO" VIRTUAL_ENV="$RELEASE_HATCH_REPO/.venv" just devenv

JOB_SERVER_TOKEN="$("$VIRTUAL_ENV/bin/python" manage.py shell << EOF
from jobserver.models.backends import Backend

backend, created = Backend.objects.get_or_create(
    slug="local-dev",
    name="Local Dev"
)
backend.level_4_url = "$RELEASE_HATCH_URL"
backend.save()
print(backend.auth_token)
EOF
)"

JOB_SERVER_ENDPOINT="$("$VIRTUAL_ENV/bin/python" manage.py shell -c 'from django.conf import settings; print(settings.BASE_URL)')"

cat > "$RELEASE_HATCH_REPO/.env" << EOF
JOB_SERVER_TOKEN=$JOB_SERVER_TOKEN
JOB_SERVER_ENDPOINT=$JOB_SERVER_ENDPOINT
RELEASE_HOST=$RELEASE_HATCH_URL
WORKSPACES=$WORKSPACE_DIR
EOF
cat "$RELEASE_HATCH_REPO/.env"

env -C "$RELEASE_HATCH_REPO" VIRTUAL_ENV="$RELEASE_HATCH_REPO/.venv" just run
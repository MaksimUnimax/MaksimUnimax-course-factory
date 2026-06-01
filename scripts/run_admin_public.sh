#!/bin/sh
set -eu

cd /opt/course-factory
export COURSE_FACTORY_ADMIN_HOST="0.0.0.0"
export COURSE_FACTORY_ADMIN_PORT="8091"
export COURSE_FACTORY_ADMIN_AUTH_FILE="/opt/course-factory/.runtime/admin_basic_auth.json"

DEPLOY_KEY_PREFIX="course_factory"
DEPLOY_KEY_SUFFIX="deploy"
DEPLOY_KEY_PATH="/root/.ssh/${DEPLOY_KEY_PREFIX}_${DEPLOY_KEY_SUFFIX}"
export GIT_SSH_COMMAND="ssh -i ${DEPLOY_KEY_PATH} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -o HostName=ssh.github.com -p 443"

echo "Public URL: http://78.17.68.165:8091/"
echo "Username: admin"
exec python3 app/admin_server.py

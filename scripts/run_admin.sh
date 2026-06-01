#!/bin/sh
set -eu

cd /opt/course-factory
DEPLOY_KEY_PREFIX="course_factory"
DEPLOY_KEY_SUFFIX="deploy"
DEPLOY_KEY_PATH="/root/.ssh/${DEPLOY_KEY_PREFIX}_${DEPLOY_KEY_SUFFIX}"
export GIT_SSH_COMMAND="ssh -i ${DEPLOY_KEY_PATH} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -o HostName=ssh.github.com -p 443"
echo "Course Factory Agent Admin local URL: http://127.0.0.1:8091"
exec python3 app/admin_server.py

#!/bin/sh
set -eu

cd /opt/course-factory
export COURSE_FACTORY_ADMIN_HOST="127.0.0.1"
export COURSE_FACTORY_ADMIN_PORT="8091"
export COURSE_FACTORY_ADMIN_AUTH_FILE="/opt/course-factory/.runtime/admin_basic_auth.json"
echo "Course Factory Agent Admin local URL: http://127.0.0.1:8091"
exec python3 app/admin_server.py

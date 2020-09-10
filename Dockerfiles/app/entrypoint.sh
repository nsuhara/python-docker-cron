#!/bin/bash

sleep 5
# set qiita access token to environment variable
source /code/config/qiita_access_token
# migrate database
alembic upgrade head
# run script at 23:00, 0 23 * * * /code/qiita.sh  >> /var/log/cron.log 2>&1
busybox crond -l 8 -L /dev/stderr -f

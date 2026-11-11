#!/bin/bash
set -euo pipefail
export AWS_REGION=ap-southeast-2
TS=$(date -u +%Y%m%dT%H%M%SZ)
B=s3://pugad-backups-hm123
docker exec chat-mongodb mongodump --db LibreChat --archive --gzip > /tmp/mongo-$TS.gz
aws s3 cp /tmp/mongo-$TS.gz $B/mongo/
tar czf /tmp/config-$TS.tgz -C /opt/pugad/LibreChat .env
aws s3 cp /tmp/config-$TS.tgz $B/config/
rm -f /tmp/mongo-$TS.gz /tmp/config-$TS.tgz
echo "$TS backup ok" >> /var/log/pugad/backup.log

#!/bin/bash
set -euo pipefail
export AWS_REGION=ap-southeast-2
REPO=/opt/pugad/repo
APP=/opt/pugad/LibreChat
BUCKET=pugad-content-hm123

# 1. Secrets from Parameter Store (kept in memory only, never written to disk)
for n in GOOGLE_KEY JWT_SECRET JWT_REFRESH_SECRET CREDS_KEY CREDS_IV; do
  export "$n"="$(aws ssm get-parameter --name "/sam10/$n" --with-decryption \
    --query Parameter.Value --output text)"
done
export APP_VERSION="$(git -C "$REPO" rev-parse --short HEAD)"

# 2. Documents from S3 (the AWS integration)
mkdir -p /opt/pugad/content
aws s3 sync "s3://$BUCKET/" /opt/pugad/content/ --delete

# 3. Config files from the repo
cp "$REPO/librechat/docker-compose.override.server.yml" "$APP/docker-compose.override.yml"
cp -r "$REPO/librechat/nginx" "$REPO/librechat/branding" "$APP/"
python3 "$REPO/scripts/build-config.py" /opt/pugad/content \
  "$REPO/librechat/librechat.template.yaml" "$APP/librechat.yaml"

# 4. Start
cd "$APP"
docker compose up -d --force-recreate
echo "$(date -u +%FT%TZ) started version $APP_VERSION"

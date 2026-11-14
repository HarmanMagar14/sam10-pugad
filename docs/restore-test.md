# Restore test (E-11): 15 Nov 2026

**Goal:** prove the nightly MongoDB backup in S3 can be restored on a different machine, and that it holds the real data.

## Result: PASS (on the second backup)

| | Attempt 1 | Attempt 2 |
|---|---|---|
| Backup file | `mongo-20261113T180004Z.gz` (10.5 KB, nightly 02:00 PHT) | `mongo-20261114T160442Z.gz` (15.7 KB, run by hand 00:04 PHT) |
| Restored on | Laptop (WSL Ubuntu), throwaway `mongo:8` container | same |
| `mongorestore` | 58 restored, 0 failed | 67 restored, 0 failed |
| users / convos / messages | **0 / 0 / 0** | **1 / 1 / 2** |
| Live server at the time | 1 / 1 / 2 | 1 / 1 / 2 |
| Matches live? | No | **Yes** |

## What attempt 1 taught us
The first restore "succeeded" (no errors) but contained no users or chats. Checking the live server showed 1 user, 1 conversation and 2 messages, and that the backup script targets the right database (`LibreChat`, same as the app's `MONGO_URI`). The account had simply been created *after* that night's 02:00 backup.

**Lesson:** a restore with no errors is not proof. Always compare restored counts against the live database.

## Steps used
Server (Session Manager), live counts and a fresh backup:
```
sudo docker exec chat-mongodb mongosh LibreChat --quiet --eval 'print(db.users.countDocuments(), db.conversations.countDocuments(), db.messages.countDocuments())'
sudo systemctl start pugad-backup.service
tail -3 /var/log/pugad/backup.log
```
Download the newest file from S3 (`pugad-backups-hm123/mongo/`) in the console. The server's IAM role can only *upload* backups, not read them (least privilege).

Laptop (Ubuntu):
```
docker run -d --name restore-test mongo:8
docker cp mongo-<TS>.gz restore-test:/tmp/backup.gz
docker exec restore-test mongorestore --gzip --archive=/tmp/backup.gz
docker exec restore-test mongosh LibreChat --quiet --eval 'print("users=" + db.users.countDocuments(), "convos=" + db.conversations.countDocuments(), "messages=" + db.messages.countDocuments())'
docker rm -f restore-test && rm -rf ~/sam10/restore-test   # backup holds account data
```

## Recovery numbers
- **RPO** (data you could lose): up to 24 h, since backups run nightly at 18:00 UTC (02:00 PHT).
- **RTO** (time to restore the database): about 5 minutes once the file is downloaded.

## Evidence
E-11a S3 backup list · E-11b live counts + fresh backup · E-11c `mongorestore` 0 failed · E-11d counts match (email blurred)

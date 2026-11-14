# Runbook: Disk filling up on pugad-server

**Alarm:** `pugad-disk-filling` (SAM10 `disk_used_percent` on `/` above 85% for 5 minutes)
**Who gets it:** pugad-alerts email
**Why it matters:** at 100% MongoDB cannot write, so sign-ins, chats and the nightly backup fail.

## 1. Confirm (2 min)
Connect: EC2 > pugad-server > Connect > Session Manager, then:
```
sudo su - ec2-user
df -h /
```
If Use% is above 85%, continue. If not, the spike already passed: check the dashboard `pugad-ops` Disk % widget.

## 2. Find what is big (5 min)
Work down from the top, following the biggest folder each time:
```
sudo du -xh / --max-depth=1 2>/dev/null | sort -h | tail -5
sudo du -xh /var/log --max-depth=1 2>/dev/null | sort -h | tail -5
ls -lhS /var/log/pugad/ | head
docker system df
```
Usual suspects:
| Where | What | Safe fix |
|---|---|---|
| `/var/log/pugad/` | app/nginx/debug logs | delete or truncate the runaway file |
| `/var/lib/docker/containers/` | container json logs | `sudo truncate -s 0 <file>-json.log` |
| `/var/lib/docker/` (images) | old images after updates | `docker image prune -a` |
| `/home/ec2-user/dumps` or `/tmp` | leftover mongodump files | delete after checking S3 has the backup |

**Never delete** anything in the MongoDB data volume or `/opt/pugad/LibreChat/.env`.

## 3. Fix (2 min)
Remove or empty the file you found, e.g.:
```
sudo rm /var/log/pugad/debug.log        # or: sudo truncate -s 0 <file>
df -h /
```
If a running process still holds a deleted file open, the space does not come back:
`sudo lsof +L1 | head` then restart that container (`docker restart <name>`).

## 4. Check the service
Open https://13-239-67-10.sslip.io, sign in, ask one question. The alarm returns to OK within about 10 minutes.

## 5. Prevent it again
- logrotate rule `/etc/logrotate.d/pugad` (copy of `infra/logrotate-pugad`): daily, max 100 MB per file, keep 7, compressed.
- logrotate runs hourly (systemd timer override) so `maxsize` is checked often.
- Write a short incident note: start time, alarm time, cause, fix time, what changed.

## Incident record: staged fault, 14 Nov 2026 (times UTC)
| Item | Value |
|---|---|
| Fault started | 15:40 (debug.log begins growing in /var/log/pugad) |
| Crossed 85% | 15:50 (88%), peaked 93% at 15:51 |
| Alarm email received | 15:54:06 (`pugad-disk-filling`, datapoint 87.2%) |
| Root cause found | 15:55:10 (`du` trail: / 19G -> /var 14G -> /var/log/pugad 9.1G -> debug.log 9.0G) |
| Fixed (disk back to 48%) | 15:55:44 (`rm /var/log/pugad/debug.log`) |
| Prevention in place | 15:56 (logrotate rule + hourly timer, dry run clean) |
| Alarm back to OK | (fill in from alarm History) |
| Time to detect | ~4 min after crossing 85% (alarm uses a 5-minute average) |
| Time to fix after alarm | ~2 min |
| Root cause | A debug log in /var/log/pugad grew with no size limit or rotation |
| Prevention | `/etc/logrotate.d/pugad`: daily, maxsize 100M, keep 7, compress; logrotate timer changed to hourly |
| Note | XFS `fallocate` reserves the full new size when growing a file, so the fill had to be done in 1 GB appended chunks; space after `rm` is freed a few seconds later, not instantly |

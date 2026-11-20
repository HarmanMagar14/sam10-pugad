# Pugad Assist — SAM10 Final Project
A reskin of LibreChat for an invented egg supplier, deployed and operated on AWS.

## Credits
Based on LibreChat by Danny Avila and contributors — https://github.com/danny-avila/LibreChat — MIT licence.

## Project website
The report site lives in its own folder, `website/`, and is published to GitHub Pages at
https://harmanmagar14.github.io/sam10-pugad/ by `.github/workflows/pages.yml` on every push to `main`.
One-time setup: Settings > Pages > Build and deployment > Source: **GitHub Actions**.

To change it, edit `scripts/build-site.py` and run `python scripts/build-site.py` (it rewrites `website/`).
Remaining fill-ins (declaration date, video link) are at the top of that file. Screenshots used by the site
are in `website/evidence/`.

## Contribution log
| Date | Who | What | Evidence |
|---|---|---|---|
| 2026-11-06 | Harman | Set up laptop tools (WSL, Docker, Git, gitleaks); created GitHub repo | — |
| 2026-11-06 | Harman | Created AWS account (Builder ID with MFA, Sydney region, USD 25 budget) | E-12, E-16 |
| 2026-11-06 | Justine | Ran original LibreChat v0.8.9-rc1 locally | E-05 |
| 2026-11-06 | Justine | Pugad Assist reskin running locally: logo, wording, 10 invented documents, system prompt | E-01 |
| 2026-11-06 | Justine | Tested Gemini models (2.5-flash retired, 3.8-flash timed out), chose gemini-3.5-flash; 5/5 test questions correct | test screenshots |
| 2026-11-06 | Justine | Pugad colour theme (warm brown/yolk, light and dark); slim stack 785 MiB | E-01 |
| 2026-11-06 | Harman | S3 content + backup buckets (versioned, private); 5 secrets in Parameter Store | E-13 |
| 2026-11-06 | Harman | Created pugad-ec2-role with least-privilege inline policy | role screenshot |
| 2026-11-06 | Harman | Security group pugad-web: HTTP from CloudFront prefix list only | SG screenshot |
| 2026-11-07 | Justine | Log groups with 1-month retention (requests, app, mongodb) | log groups screenshot |
| 2026-11-07 | Harman | CloudTrail pugad-trail logging; SNS topic pugad-alerts (email confirmed) | trail screenshot |
| 2026-11-10 | Harman | CloudFront blocked by account verification (4+ days); Plan B: Caddy + Let's Encrypt HTTPS at https://13-239-67-10.sslip.io | E-02 |
| 2026-11-10 | Harman | Security group: HTTP 80 + HTTPS 443 from anywhere (Caddy); registration closed after team sign-up | SG screenshot |
| 2026-11-10 | Justine | CloudWatch dashboard `pugad-ops` (alarm strip, questions, answer time, failures, CPU, memory, disk) | evidence/E-06-dashboard.jpg |
| 2026-11-10 | Harman | CPU stress test: real ALARM email from `pugad-high-cpu` | evidence/E-08 (CPU email) |
| 2026-11-10 | Harman | Automation #2: health-check Lambda every 15 min + `pugad-site-down` alarm, least-privilege role | infra/health-check/, evidence/E-09, E-09b |
| 2026-11-10 | Harman | Staged disk-full fault: alarm, root cause, fix, logrotate guard, runbook | docs/runbook-disk-full.md, infra/logrotate-pugad, evidence/E-12a–c |
| 2026-11-11 | Justine | Restore test of S3 backup on laptop (2nd backup matched live: 1/1/2) | docs/restore-test.md, evidence/E-11a–c |

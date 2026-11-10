# Pugad Assist — SAM10 Final Project
A reskin of LibreChat for an invented egg supplier, deployed and operated on AWS.

## Credits
Based on LibreChat by Danny Avila and contributors — https://github.com/danny-avila/LibreChat — MIT licence.

## Contribution log
| Date | Who | What | Evidence |
|---|---|---|---|
| 2026-11-10 | Harman | Set up laptop tools (WSL, Docker, Git, gitleaks); created GitHub repo | — |
| 2026-11-10 | Harman | Created AWS account (Builder ID with MFA, Sydney region, USD 25 budget) | E-12, E-16 |
| 2026-11-10 | Justine | Ran original LibreChat v0.8.9-rc1 locally | E-05 |
| 2026-11-10 | Harman | Pugad Assist reskin running locally: logo, wording, 10 invented documents, system prompt | E-01 |
| 2026-11-10 | Justine | Tested Gemini models (2.5-flash retired, 3.8-flash timed out), chose gemini-3.5-flash; 5/5 test questions correct | test screenshots |
| 2026-11-10 | Harman | Pugad colour theme (warm brown/yolk, light and dark); slim stack 785 MiB | E-01 |
| 2026-11-10 | Harman | S3 content + backup buckets (versioned, private); 5 secrets in Parameter Store | E-13 |
| 2026-11-10 | Harman | Created pugad-ec2-role with least-privilege inline policy | role screenshot |
| 2026-11-10 | Harman | Security group pugad-web: HTTP from CloudFront prefix list only | SG screenshot |

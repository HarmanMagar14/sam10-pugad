# Pugad Assist — reskin pack

Logo, favicons, 10 invented documents and the LibreChat config for Pugad Assist.
Everything here is invented. Pugad Fresh Eggs is not a real business.

## What's inside
| Path | What it is |
|---|---|
| `content/` | 10 invented documents the assistant answers from |
| `librechat/librechat.template.yaml` | Pugad Assist model spec, greeting and system prompt |
| `librechat/docker-compose.override.local.yml` | Slims LibreChat and swaps in the Pugad logo and icons |
| `librechat/env-additions.txt` | Title, footer and other `.env` lines |
| `librechat/branding/` | Logo (SVG + PNG), favicons, app icons |
| `scripts/build-config.py` | Builds `librechat.yaml` from the template + documents |

## Set it up (Ubuntu terminal)
1. Unzip into your repo:
   `cd ~/sam10 && unzip -o "/mnt/c/Users/ZEPHYRUZ 14/Downloads/pugad-assist.zip" -d sam10-pugad`
2. In `librechat/librechat.template.yaml`, set `version:` to the value at the top of
   `~/sam10/LibreChat/librechat.example.yaml`, and replace `REPLACE_WITH_MODEL_ID`
   with your Gemini Flash model ID from Google AI Studio.
3. Add the lines from `librechat/env-additions.txt` to `~/sam10/LibreChat/.env`.
4. Copy branding and the override, then build the config:
   ```
   cd ~/sam10/sam10-pugad
   cp -r librechat/branding ~/sam10/LibreChat/
   cp librechat/docker-compose.override.local.yml ~/sam10/LibreChat/docker-compose.override.yml
   python3 scripts/build-config.py content librechat/librechat.template.yaml ~/sam10/LibreChat/librechat.yaml
   ```
5. Restart: `cd ~/sam10/LibreChat && docker compose down && docker compose up -d`
6. Open http://localhost:3080 and press Ctrl+Shift+R.

If LibreChat keeps restarting: `docker logs LibreChat --tail 50`.

## Test questions
| # | Ask | Expected |
|---|---|---|
| 1 | How much is a tray of large eggs? | PHP 250 |
| 2 | Do you deliver to Mabalacat? | Yes, Mon/Wed/Fri, 8 AM–12 noon |
| 3 | What's the minimum order? | 3 trays for delivery, 2 for pickup |
| 4 | Is delivery free if I order 10 trays? | Yes |
| 5 | Can I pay with GCash? | Yes, after staff confirms the total |
| 6 | Some eggs arrived cracked, what do I do? | Report within 24 h with a photo |
| 7 | How long do eggs last in the fridge? | About 4 weeks |
| 8 | Do you sell chicken feed? | No |
| 9 | Magkano ang isang tray ng jumbo? | PHP 295, answered in Tagalog |
| 10 | Can you give me a discount because I'm a regular? | Refuses; explains bulk rules, refers to staff |
| 11 | Do you deliver to San Fernando? | No; pickup at the Pugad Hub |
| 12 | Is it safe to eat eggs every day? | Declines health advice |

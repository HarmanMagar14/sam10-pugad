#!/usr/bin/env python3
"""Builds the Pugad Assist project website into website/ (deployed to GitHub Pages by .github/workflows/pages.yml).

Usage:  python scripts/build-site.py
Edit the page text in this file, then run it again. Everything the team still
has to fill in is in the FILL-IN section just below, and shows on the site as
a dashed grey placeholder until it is set.
"""
from pathlib import Path
import html

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "website"
REPO = "https://github.com/HarmanMagar14/sam10-pugad"

# ---------------------------------------------------------------------------
# FILL-IN: set these, then re-run the script.
# ---------------------------------------------------------------------------
JUSTINE_FULL_NAME = "Justine Esguerra"
HARMAN_FULL_NAME = "Harman Magar"
FOOTER_EMAILS = ["esguerra.justinegabriel@student.auf.edu.ph", "magar.harman@student.auf.edu.ph"]  # shown in the footer
DECLARATION_DATE = "16 November 2026"
VIDEO_URL = "https://www.youtube.com/embed/mSTSRLhWWG0"  # YouTube embed URL (watch?v=… link converted to /embed/…)
# Monthly cost in USD per service. Everything ran inside the AWS Free Tier, so all are 0.
COST_AFTER = {
    "EC2 (server + 20 GB disk)": 0.0,
    "CloudWatch (logs, metrics, alarms, dashboard)": 0.0,
    "S3 (content + backups)": 0.0,
    "Lambda + EventBridge Scheduler": 0.0,
    "Other (data transfer, CloudTrail, SNS, tax)": 0.0,
}
COST_PERIOD = "Nov 2026, AWS Free Tier"

# ---------------------------------------------------------------------------
# Evidence register: id -> (file in website/evidence, short caption)
# ---------------------------------------------------------------------------
EV = {
    "E-01": ("E-01-pugad-assist.png", "Pugad Assist answering a price question with the Pugad branding"),
    "E-05": ("E-05-original-librechat.webp", "The original, un-branded LibreChat running on the laptop (baseline)"),
    "E-06": ("E-06-dashboard.jpg", "CloudWatch dashboard pugad-ops: alarm strip, questions, answer time, failures, CPU, memory, disk"),
    "E-07": ("E-07-alarms.jpg", "The 8 CloudWatch alarms, all with actions enabled (14 Nov 2026)"),
    "E-09": ("E-09-lambda-test.jpg", "Health-check Lambda manual test: status 200, ok 1, latency 0.638 s"),
    "E-09b": ("E-09b-lambda-schedule.jpg", "Health-check Lambda triggered by Scheduler every 15 minutes (rate(15 minutes), ENABLED)"),
    "E-10": ("E-10-backup-lifecycle.png", "S3 lifecycle rule expire-old-backups on the backup bucket"),
    "E-11a": ("E-11a-backups-in-s3.jpg", "Nightly MongoDB backups in s3://pugad-backups-hm123/mongo/"),
    "E-11b": ("E-11b-live-counts-and-fresh-backup.jpg", "Live database counts (users 1, convos 1, messages 2) and a fresh backup run"),
    "E-12": ("E-12-builder-id-mfa-redacted.png", "AWS Builder ID with an MFA (TOTP) device registered (personal details blacked out)"),
    "E-12a": ("E-12a-disk-fill.jpg", "Staged fault: debug.log grows, disk climbs 73% → 93%"),
    "E-12b": ("E-12b-disk-diagnosis.jpg", "Diagnosis at 15:55:10 UTC: du trail / → /var → /var/log/pugad → debug.log 9.0 G"),
    "E-12c": ("E-12c-logrotate.jpg", "Prevention: logrotate rule dry run (maxsize 100 MB) and hourly timer"),
    "E-13": ("E-13-gemini-429-daily-quota.jpg", "Known limit: Gemini free-tier daily quota reached (status 429)"),
    "E-14": ("E-14-quality-guardrails.jpg", "Guardrails: refuses an unknown fact and a prompt-injection attempt"),
    "E-15a": ("E-15a-healthcheck-runs.jpg", "Logs Insights: health-check runs every 15 min, HealthCheckOK 1, status 200"),
    "E-15b": ("E-15b-backup-runs.jpg", "Logs Insights: 5 'backup ok' runs, 11–14 Nov 2026"),
    "E-16": ("E-16-budget-before.png", "Budget pugad-monthly-budget: USD 25, USD 0.00 used (before)"),
    "LOGS": ("log-groups.png", "CloudWatch log groups /sam10/pugad/requests, /app and /mongodb"),
    "DECL": ("declaration-signed.png", "Declaration signed by both team members, 16 Nov 2026"),
}

PAGES = [
    ("index.html", "Summary", "Executive summary"),
    ("architecture.html", "Architecture", "AWS infrastructure design"),
    ("system-card.html", "System card", "System card"),
    ("baseline.html", "Baseline", "Baseline: before we started"),
    ("well-architected.html", "Well-Architected", "Well-Architected review"),
    ("operations.html", "Monitoring & security", "Monitoring, backup & restore, security"),
    ("automation.html", "Automation & incident", "Automation and the incident"),
    ("results.html", "Results", "Results: before and after"),
    ("next-steps.html", "Next steps", "Next steps"),
    ("evidence.html", "Evidence", "Evidence register"),
    ("declaration.html", "Declaration & video", "Declaration and video"),
]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def esc(s):
    return html.escape(str(s))


def ev(*ids):
    """Evidence tag(s) placed right next to a claim."""
    out = []
    for i in ids:
        f, cap = EV[i]
        out.append(f'<a class="ev-tag" href="evidence/{f}" title="{esc(cap)}" target="_blank" rel="noopener">{i}</a>')
    return "".join(out)


def fig(i, extra=""):
    f, cap = EV[i]
    return (f'<figure class="ev" id="{i}"><a class="img" href="evidence/{f}" target="_blank" rel="noopener">'
            f'<img src="evidence/{f}" alt="{esc(cap)}" loading="lazy"></a>'
            f'<figcaption><b>{i}</b> · {esc(cap)}{(" " + extra) if extra else ""}</figcaption></figure>')


def todo(text="to fill in"):
    return f'<span class="todo">{esc(text)}</span>'


def filled(value, placeholder):
    return esc(value) if value else todo(placeholder)


def table(head, rows, num_cols=()):
    th = "".join(f'<th{" class=num" if i in num_cols else ""}>{h}</th>' for i, h in enumerate(head))
    trs = "".join("<tr>" + "".join(f'<td{" class=num" if i in num_cols else ""}>{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def r(kind):
    label = {"good": "Good", "adequate": "Adequate", "gap": "Gap"}[kind]
    return f'<span class="rating {kind}">{label}</span>'


# ---------------------------------------------------------------------------
# charts (inline SVG, styled by site.css, hover tooltips via data-tip)
# ---------------------------------------------------------------------------
def disk_chart():
    # Real readings from E-12a / E-12b / runbook (UTC, 14 Nov 2026)
    pts = [("15:47", 1, 73, "before the fault was pushed further"), ("15:48", 2, 78, ""),
           ("15:49", 3, 83, ""), ("15:50", 4, 88, "crossed the 85% alarm line"),
           ("15:51", 5, 93, "peak"), ("15:55:10", 9.17, 93, "root cause found (du trail)"),
           ("15:55:44", 9.73, 48, "debug.log deleted, disk back to 48%")]
    W, H, L, R_, T, B = 760, 300, 44, 16, 20, 36
    x0, x1 = 0, 11  # minutes after 15:46
    sx = lambda m: L + (m - x0) / (x1 - x0) * (W - L - R_)
    sy = lambda p: T + (100 - p) / 100 * (H - T - B)
    g = []
    for p in (0, 25, 50, 75, 100):
        g.append(f'<line class="grid-line" x1="{L}" x2="{W-R_}" y1="{sy(p)}" y2="{sy(p)}"/>'
                 f'<text class="axis-label" x="{L-8}" y="{sy(p)+4}" text-anchor="end">{p}%</text>')
    for m, lab in ((0, "15:46"), (2, "15:48"), (4, "15:50"), (6, "15:52"), (8, "15:54"), (10, "15:56")):
        g.append(f'<text class="axis-label" x="{sx(m)}" y="{H-12}" text-anchor="middle">{lab}</text>')
    g.append(f'<line class="threshold" x1="{L}" x2="{W-R_}" y1="{sy(85)}" y2="{sy(85)}"/>'
             f'<text class="threshold-label" x="{W-R_}" y="{sy(85)-6}" text-anchor="end">alarm line 85%</text>')
    am = 8.1  # alarm email 15:54:06
    g.append(f'<line class="grid-line" x1="{sx(am)}" x2="{sx(am)}" y1="{T}" y2="{H-B}" stroke-dasharray="3 3"/>'
             f'<text class="annot" x="{sx(am)-6}" y="{sy(30)}" text-anchor="end">alarm email</text>'
             f'<text class="annot" x="{sx(am)-6}" y="{sy(30)+15}" text-anchor="end">15:54:06</text>')
    path = " ".join(("M" if i == 0 else "L") + f"{sx(m):.1f},{sy(p):.1f}" for i, (_, m, p, _) in enumerate(pts))
    g.append(f'<path class="series" d="{path}"/>')
    for t, m, p, note in pts:
        tip = f"{t} UTC — {p}% used" + (f" ({note})" if note else "")
        g.append(f'<circle class="dot" cx="{sx(m):.1f}" cy="{sy(p):.1f}" r="5"/>'
                 f'<circle class="hit" cx="{sx(m):.1f}" cy="{sy(p):.1f}" r="16" data-tip="{esc(tip)}"/>')
    g.append(f'<text class="val" x="{sx(5)}" y="{sy(93)-12}" text-anchor="middle">93%</text>'
             f'<text class="val" x="{sx(9.73)+8}" y="{sy(48)+4}">48% after fix</text>')
    svg = f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Disk used percent during the staged disk-full fault">{"".join(g)}</svg>'
    rows = "".join(f"<tr><td>{t}</td><td class=num>{p}%</td><td>{esc(n)}</td></tr>" for t, _, p, n in pts)
    return (f'<div class="card chart"><p class="chart-title">Disk used on pugad-server, 14 Nov 2026 (UTC)</p>'
            f'<p class="chart-sub">Before the fix: climbing to 93%. After the fix: 48%. Hover a point for details. '
            f'Source {ev("E-12a", "E-12b")}</p>{svg}'
            f'<details class="data-table"><summary>Show as a table</summary>'
            f'<div class="table-wrap"><table><thead><tr><th>Time</th><th class=num>Disk used</th><th>Note</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></details></div>')


def bar_chart(title, sub, items, unit="", aria=""):
    """items: list of (label, value, highlight, tooltip)"""
    W, H, L, T, B = 760, 230, 10, 24, 44
    vmax = max(v for _, v, _, _ in items) or 1
    n = len(items)
    slot = (W - 2 * L) / n
    bw = min(120, slot * 0.5)
    g = [f'<line class="grid-line" x1="{L}" x2="{W-L}" y1="{H-B}" y2="{H-B}"/>']
    for i, (lab, v, hi, tip) in enumerate(items):
        cx = L + slot * (i + .5)
        h = (H - T - B) * v / vmax
        y = H - B - h
        cls = "bar" if hi else "bar muted"
        if h > 0:
            rr = min(4, h)
            g.append(f'<path class="{cls}" d="M{cx-bw/2},{H-B} V{y+rr} Q{cx-bw/2},{y} {cx-bw/2+rr},{y} '
                     f'H{cx+bw/2-rr} Q{cx+bw/2},{y} {cx+bw/2},{y+rr} V{H-B} Z"/>')
        g.append(f'<rect class="hit" x="{cx-slot/2}" y="{T}" width="{slot}" height="{H-T-B}" data-tip="{esc(tip)}"/>')
        g.append(f'<text class="val" x="{cx}" y="{y-8}" text-anchor="middle">{v:g}{unit}</text>')
        g.append(f'<text class="axis-label" x="{cx}" y="{H-B+20}" text-anchor="middle">{esc(lab)}</text>')
    svg = f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(aria or title)}">{"".join(g)}</svg>'
    return f'<div class="card chart"><p class="chart-title">{title}</p><p class="chart-sub">{sub}</p>{svg}</div>'


def cost_block():
    vals = [v for v in COST_AFTER.values() if v is not None]
    rows = [[esc(k), f"USD {v:.2f}" if v is not None else todo()] for k, v in COST_AFTER.items()]
    total = sum(vals) if len(vals) == len(COST_AFTER) else None
    rows.append(["<b>Total</b>", f"<b>USD {total:.2f}</b>" if total is not None else todo()])
    rows.append(["Budget (alert at USD 25)", "USD 25.00"])
    t = table(["Service", f"After ({filled(COST_PERIOD, 'period')})"], rows, num_cols=(1,))
    if total is not None:
        chart = bar_chart("Monthly AWS cost: before vs after", "USD. Before = 10 Nov 2026 budget page; after = November 2026, all usage inside the AWS Free Tier.",
                          [("Before (10 Nov)", 0, False, "USD 0.00 used — E-16"),
                           (f"After ({COST_PERIOD})", round(total, 2), True, f"USD {total:.2f}, everything inside the AWS Free Tier"),
                           ("Budget limit", 25, False, "USD 25 monthly budget with email alert")], unit="")
    else:
        chart = ('<div class="todo-block"><b>Cost chart appears here automatically</b> once the numbers in '
                 '<code>COST_AFTER</code> in <code>scripts/build-site.py</code> are filled in from '
                 'Billing → Cost Explorer (group by Service) and the script is re-run.</div>')
    return t + chart


# ---------------------------------------------------------------------------
# architecture diagram
# ---------------------------------------------------------------------------
ARCH_SVG = """
<style>
.arch .zone{fill:none;stroke:var(--line);stroke-width:1.5;stroke-dasharray:6 4}
.arch .box{fill:var(--surface);stroke:var(--brand);stroke-width:1.5}
.arch .box.alt{fill:var(--surface-2);stroke:var(--line)}
.arch .box.ext{fill:var(--surface);stroke:var(--muted);stroke-dasharray:4 3}
.arch text{fill:var(--ink);font:13px var(--font)}
.arch .t{font-weight:700}
.arch .s{fill:var(--muted);font-size:11.5px}
.arch .z{fill:var(--muted);font-size:12px;font-weight:700;letter-spacing:.05em}
.arch .ln{stroke:var(--ink-2);stroke-width:1.5;fill:none;marker-end:url(#ah)}
.arch .ln.d{stroke-dasharray:4 3}
.arch .lb{fill:var(--brand-ink);font-size:11.5px;font-weight:600}
</style>
<svg class="arch" viewBox="0 0 960 640" role="img" aria-label="Pugad Assist architecture on AWS">
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor" style="color:var(--ink-2)"/></marker></defs>

<!-- outside AWS -->
<rect class="box ext" x="20" y="40" width="170" height="70" rx="10"/>
<text class="t" x="105" y="70" text-anchor="middle">Customer</text>
<text class="s" x="105" y="90" text-anchor="middle">web browser / phone</text>

<rect class="box ext" x="20" y="470" width="170" height="80" rx="10"/>
<text class="t" x="105" y="500" text-anchor="middle">Google Gemini</text>
<text class="s" x="105" y="518" text-anchor="middle">gemini-3.5-flash</text>
<text class="s" x="105" y="534" text-anchor="middle">(outside AWS)</text>

<rect class="box ext" x="20" y="580" width="170" height="44" rx="10"/>
<text class="t" x="105" y="607" text-anchor="middle">Team email</text>

<!-- AWS region -->
<rect class="zone" x="220" y="14" width="725" height="616" rx="14"/>
<text class="z" x="236" y="36">AWS · ap-southeast-2 (Sydney)</text>

<!-- EC2 -->
<rect class="zone" x="240" y="56" width="330" height="390" rx="12" style="stroke:var(--brand)"/>
<text class="z" x="256" y="78">EC2 · pugad-server · 20 GB disk</text>
<rect class="box" x="265" y="92" width="280" height="54" rx="8"/>
<text class="t" x="280" y="115">Caddy</text><text class="s" x="280" y="133">HTTPS 443 · free Let's Encrypt certificate</text>
<rect class="box" x="265" y="166" width="280" height="54" rx="8"/>
<text class="t" x="280" y="189">nginx</text><text class="s" x="280" y="207">writes request log (JSON) to /var/log/pugad</text>
<rect class="box" x="265" y="240" width="280" height="54" rx="8"/>
<text class="t" x="280" y="263">LibreChat (Pugad Assist)</text><text class="s" x="280" y="281">reskinned chat app + system prompt</text>
<rect class="box" x="265" y="314" width="280" height="54" rx="8"/>
<text class="t" x="280" y="337">MongoDB</text><text class="s" x="280" y="355">users, conversations, messages</text>
<rect class="box alt" x="265" y="384" width="280" height="46" rx="8"/>
<text class="s" x="280" y="403">systemd: pugad.service · pugad-backup.timer</text>
<text class="s" x="280" y="420">CloudWatch agent · logrotate (hourly)</text>
<path class="ln" d="M405,146 V164"/><path class="ln" d="M405,220 V238"/><path class="ln" d="M405,294 V312"/>

<!-- arrows from outside -->
<path class="ln" d="M190,75 H230 Q245,75 245,95 V110 H263"/>
<text class="lb" x="196" y="66">HTTPS</text>
<path class="ln d" d="M265,267 H215 Q205,267 205,280 V500 H192"/>
<text class="lb" x="128" y="455">question + documents</text>

<!-- data services -->
<rect class="box" x="610" y="56" width="315" height="56" rx="8"/>
<text class="t" x="625" y="79">S3 · pugad-content-hm123</text><text class="s" x="625" y="97">10 shop documents, synced at start-up</text>
<rect class="box" x="610" y="126" width="315" height="56" rx="8"/>
<text class="t" x="625" y="149">SSM Parameter Store</text><text class="s" x="625" y="167">5 encrypted secrets (API key, JWT, creds)</text>
<rect class="box" x="610" y="196" width="315" height="56" rx="8"/>
<text class="t" x="625" y="219">S3 · pugad-backups-hm123</text><text class="s" x="625" y="237">nightly DB backup · versioned · lifecycle</text>
<path class="ln" d="M608,84 H572"/><path class="ln" d="M608,154 H572"/><path class="ln" d="M572,224 H608"/>
<text class="lb" x="576" y="218">02:00</text>

<!-- observability -->
<rect class="box" x="610" y="286" width="315" height="70" rx="8"/>
<text class="t" x="625" y="309">CloudWatch</text><text class="s" x="625" y="327">logs (30-day) · metrics · dashboard pugad-ops</text><text class="s" x="625" y="343">8 alarms</text>
<rect class="box" x="610" y="376" width="150" height="56" rx="8"/>
<text class="t" x="625" y="399">SNS</text><text class="s" x="625" y="417">pugad-alerts</text>
<rect class="box" x="775" y="376" width="150" height="56" rx="8"/>
<text class="t" x="790" y="399">CloudTrail</text><text class="s" x="790" y="417">pugad-trail</text>
<path class="ln" d="M572,330 H608"/><text class="lb" x="576" y="322">logs</text>
<path class="ln" d="M660,356 V374"/>
<path class="ln" d="M640,432 V600 H192"/><text class="lb" x="420" y="594">alarm email</text>

<!-- automation -->
<rect class="box" x="610" y="470" width="315" height="70" rx="8"/>
<text class="t" x="625" y="493">Lambda · pugad-health-check</text><text class="s" x="625" y="511">EventBridge Scheduler, every 15 min</text><text class="s" x="625" y="527">calls the site, writes HealthCheckOK</text>
<path class="ln d" d="M610,500 H590 V120 H547"/>
<path class="ln" d="M880,470 V358"/>

<rect class="box alt" x="250" y="470" width="320" height="56" rx="8"/>
<text class="t" x="265" y="493">IAM role pugad-ec2-role</text><text class="s" x="265" y="511">least privilege · Session Manager (no SSH)</text>
<rect class="box alt" x="250" y="540" width="320" height="44" rx="8"/>
<text class="t" x="265" y="567">AWS Budgets · USD 25 / month alert</text>
</svg>
"""


# ---------------------------------------------------------------------------
# page bodies
# ---------------------------------------------------------------------------
BODY = {}

SECTIONS = [
    ("architecture.html", "assets/architecture.svg", "AWS infrastructure design", "One server, with managed AWS services around it for secrets, backups, logs and alarms."),
    ("system-card.html", "evidence/E-14-quality-guardrails.jpg", "System card", "What Pugad Assist is, what it knows, its model, its limits, and who should not use it."),
    ("baseline.html", "evidence/E-05-original-librechat.webp", "Baseline", "Where we started: stock LibreChat on a laptop and an empty AWS account."),
    ("well-architected.html", "evidence/E-12-builder-id-mfa-redacted.png", "Well-Architected review", "Six pillars rated good, adequate or gap, and the one gap to fix first."),
    ("operations.html", "evidence/E-06-dashboard.jpg", "Monitoring, backup and security", "The dashboard, eight alarms, a proven restore, and security before and after."),
    ("automation.html", "evidence/E-12b-disk-diagnosis.jpg", "Automation and the incident", "Two automations that run on their own, and a disk-full fault fixed in two minutes."),
    ("results.html", "evidence/E-11b-live-counts-and-fresh-backup.jpg", "Results", "Before and after, with cost and graphs."),
    ("next-steps.html", "evidence/E-13-gemini-429-daily-quota.jpg", "Next steps", "Five improvements, most important first."),
    ("evidence.html", "evidence/E-09-lambda-test.jpg", "Evidence", "Every screenshot behind every claim on this site."),
    ("declaration.html", "evidence/E-01-pugad-assist.png", "Declaration and video", "Our signed declaration and the project video."),
]

ICON = {
    "chat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg>',
    "doc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    "disk": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 14h18M7 17h.01"/></svg>',
    "bell": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 1 1 12 0c0 7 3 8 3 8H3s3-1 3-8"/><path d="M10 20a2 2 0 0 0 4 0"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>',
    "image": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m21 16-5-5-9 9"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
}

CMD_ROWS = [
    ("automation.html#incident", "disk", "Automation &amp; incident", "debug.log 9.0G → fixed in ~2 min", "⌘ ↵", True),
    ("operations.html", "bell", "Monitoring &amp; alarms", "pugad-disk-filling · 15:54:06 UTC", "⌘ M", False),
    ("results.html", "chart", "Results: before and after", "detect ~4 min · fix ~2 min", "⌘ R", False),
    ("evidence.html", "image", "Evidence", "E-12a  E-12b  E-12c", "⌘ E", False),
]

BODY["index.html"] = f"""
<div class="hero-wrap">
<section class="hero">
  <span class="eyebrow"><span class="tag">SAM10</span>Live on AWS with alarms, nightly backups &amp; a health check</span>
  <h1 class="hero-title">A shop chatbot, moved to the cloud<br>and kept <span class="warm">alive</span>.</h1>
  <p class="hero-sub">Pugad Assist answers customer questions for an invented egg supplier in Pampanga.
  We put it on Amazon Web Services, then watched it, backed it up, locked it down and proved it recovers when something breaks.</p>
  <div class="keys">
    <a class="keycap" href="https://13-239-67-10.sslip.io" target="_blank" rel="noopener">{ICON["chat"]}Open Pugad Assist</a>
    <a class="keycap" href="architecture.html">{ICON["doc"]}Read the report</a>
  </div>
  <p class="mono-cap">13-239-67-10.sslip.io · ap-southeast-2 · gemini-3.5-flash</p>

  <div class="cmd" role="group" aria-label="Jump to a section">
    <div class="cmd-input">{ICON["search"]}<span class="cmd-q">disk full<span class="caret"></span></span><span class="mode">Report</span></div>
    <ul class="cmd-list">
""" + "".join(f"""      <li><a href="{h}"{' class="active"' if act else ''}><span class="ico">{ICON[ic]}</span><span>{lab}</span><span class="arg">{arg}</span><span class="kbd">{k}</span></a></li>
""" for h, ic, lab, arg, k, act in CMD_ROWS) + f"""    </ul>
    <div class="cmd-foot"><span>↑↓ navigate · ↵ open · esc dismiss</span><span class="logo"><span class="diamond"></span>Pugad Assist</span></div>
  </div>

  <a class="ghost" href="#summary">Learn more {ICON["arrow"]}</a>
</section>
<div class="badge"><span class="mark">S10</span><span><small>SAM10 final project</small><b>Built on AWS · Sydney</b></span></div>
</div>

<div class="content wide" id="summary">
<p class="kicker">Executive summary</p>
<h2 style="margin-top:0">In plain English</h2>
<ul>
  <li><b>We built the assistant.</b> It answers only from ten shop documents. {ev("E-01")}</li>
  <li><b>We rented a computer in the cloud.</b> One server in Sydney runs it, with a padlock (HTTPS).</li>
  <li><b>We watch it.</b> A dashboard and eight alarms that email us. {ev("E-06", "E-07")}</li>
  <li><b>We copy it every night</b>, and proved a copy really restores: 1 user, 1 chat, 2 messages, matching the live server. {ev("E-11b")}</li>
  <li><b>Two chores run by themselves:</b> the nightly backup, and a check of the site every 15 minutes. {ev("E-15a", "E-15b")}</li>
  <li><b>We broke it on purpose.</b> We filled the disk, got the alarm, and fixed it in about two minutes. {ev("E-12b")}</li>
  <li><b>We kept the bill small</b>, with a USD 25 monthly budget alert. {ev("E-16")}</li>
</ul>
<div class="callout bad"><b>The one thing to fix first:</b> everything runs on a single server. If it stops, the site stops until someone rebuilds it by hand.</div>

<h2>The report</h2>
<ul class="projects">
""" + "".join(f"""  <li><a href="{href}"><img src="{img}" alt="" loading="lazy"><h3>{esc(t)}</h3><p>{esc(d)}</p></a></li>
""" for href, img, t, d in SECTIONS) + f"""</ul>

<p style="margin-top:40px;color:var(--muted);font-size:.88rem">Pugad Fresh Eggs is not a real business; every price, place and contact detail is invented.
Pugad Assist is based on <a href="https://github.com/danny-avila/LibreChat">LibreChat</a> (MIT licence).</p>
</div>
"""

BODY["architecture.html"] = f"""
<p class="kicker">Section 2</p>
<h1>AWS infrastructure design</h1>
<p class="lede">One server does the work; managed AWS services around it hold the secrets, the backups, the logs and the alarms.</p>
<div class="card">{ARCH_SVG}</div>
<p style="color:var(--muted);font-size:.85rem">Solid arrows: data flows on every request or on a schedule. Dashed arrows: calls out of AWS or checks from outside the server.</p>

<h2>How a question travels</h2>
<ol>
  <li>The customer opens <code>https://13-239-67-10.sslip.io</code>. <b>Caddy</b> answers on HTTPS with a free Let's Encrypt certificate.</li>
  <li><b>nginx</b> logs the request (time, status, duration, app version) to <code>/var/log/pugad/access.log</code>, which the CloudWatch agent ships to <code>/sam10/pugad/requests</code>. {ev("LOGS")}</li>
  <li><b>LibreChat</b> adds the Pugad system prompt and the 10 shop documents and sends it all to <b>Google Gemini 3.5 Flash</b>.</li>
  <li>The answer streams back; the conversation is saved in <b>MongoDB</b> on the same server.</li>
</ol>

<h2>Each piece and why it is there</h2>
{table(["Component", "Job", "Why this choice"], [
  ["EC2 <code>pugad-server</code> (Docker Compose)", "Runs Caddy, nginx, LibreChat, MongoDB", "Simplest way to run an existing Docker app; slimmed to ~785 MiB by turning off search, RAG and the vector DB"],
  ["S3 <code>pugad-content-hm123</code>", "The 10 shop documents", "Staff can change prices without touching the server; synced at every start"],
  ["SSM Parameter Store", "5 secrets (Gemini key, JWT, creds)", "Secrets never sit in Git or on disk; read into memory at start-up"],
  ["S3 <code>pugad-backups-hm123</code>", "Nightly database + config backups", "Private, versioned, old copies expire automatically " + ev("E-10")],
  ["CloudWatch", "Logs (30-day), metrics, dashboard, 8 alarms", "One place to see health " + ev("E-06", "E-07")],
  ["SNS <code>pugad-alerts</code>", "Sends alarm emails", "Email confirmed by the team"],
  ["Lambda <code>pugad-health-check</code>", "Visits the site every 15 min", "Catches 'site down' even if the server cannot report it " + ev("E-09b")],
  ["CloudTrail <code>pugad-trail</code>", "Records every AWS console/API action", "Audit trail for security"],
  ["IAM role <code>pugad-ec2-role</code>", "Gives the server only the permissions it needs", "Least privilege: it can upload backups but not read or delete them"],
  ["AWS Budgets", "Email if spend passes USD 25 / month", "No bill shock " + ev("E-16")],
])}

<div class="callout"><b>Plan B on HTTPS.</b> The design used <b>CloudFront</b> in front of the server. AWS held the account in
verification for 4+ days, so CloudFront could not be created. We switched to Caddy with an automatic certificate on an
<code>sslip.io</code> address so the site still had HTTPS. The cost of this: ports 80 and 443 are open to the whole internet
instead of only to CloudFront (see <a href="operations.html#security">security</a>).</div>
"""

BODY["system-card.html"] = f"""
<p class="kicker">Section 3</p>
<h1>System card: Pugad Assist</h1>
<p class="lede">What it is, what it knows, what it runs on, where it fails, and who should not rely on it.</p>

<div class="grid-2">
<div class="card"><h3 style="margin-top:0">What it is</h3>
<p>A customer-service chat assistant for an invented egg supplier in Angeles City and Mabalacat City, Pampanga. It answers
questions about egg sizes, prices, ordering, bulk orders, delivery, payment, opening hours, cracked eggs and storage. {ev("E-01")}</p>
<p><b>It cannot</b> place, change or cancel orders, take payments, or give discounts. Staff do that.</p></div>
<div class="card"><h3 style="margin-top:0">The model</h3>
<ul style="padding-left:18px;margin:0">
<li>Google <b>gemini-3.5-flash</b> through Google AI Studio (free tier)</li>
<li>Temperature 0.2 (steady, not creative)</li>
<li>Chosen after testing: 2.5-flash was retired, 3.8-flash timed out; 3.5-flash got 5/5 test questions right</li>
<li>No fine-tuning: all shop knowledge is in the system prompt</li></ul></div>
</div>

<h2>Its data</h2>
{table(["Data", "Where it lives", "Notes"], [
  ["10 shop documents (about, prices, ordering, bulk, delivery, payment, hours, cracked eggs, storage, FAQ)", "Git repo + S3 content bucket", "All invented. Pasted into the system prompt on start-up"],
  ["Customer accounts, conversations, messages", "MongoDB on the server; nightly copy in S3", "Registration closed after the team signed up"],
  ["Request log (time, path, status, duration, version, request body)", "CloudWatch <code>/sam10/pugad/requests</code>, 30 days", "The request body can contain the customer's question text"],
  ["Questions sent to Gemini", "Google", "Leaves AWS. Google's free-tier terms apply"],
])}

<h2>The rules it follows</h2>
<p>From the system prompt: answer <b>only</b> from the documents; say "Sorry, I don't have that information" and give the order line otherwise;
never promise discounts, refunds or replacements; no medical or nutrition advice; never ask for card numbers, passwords or PINs;
reply in English, Tagalog or Taglish; keep answers to 1–4 sentences with prices in PHP.</p>
<p>Tested with 12 questions (prices, delivery areas, minimum order, GCash, cracked eggs, Tagalog, a discount request, health advice).
It also refused to reveal its system prompt and refused an unknown fact. {ev("E-14")}</p>
{fig("E-14")}

<h2>Known limits</h2>
<ul>
<li><b>Free-tier quota.</b> When Google's daily quota runs out, the assistant shows "status 429" instead of an answer. {ev("E-13")}</li>
<li><b>Slow answers.</b> One answer on the dashboard took about 27 seconds. {ev("E-06")}</li>
<li><b>One server.</b> No automatic failover; if the server stops, the site stops.</li>
<li><b>Knowledge is frozen</b> until someone updates the documents and restarts the app. It does not know today's stock or delivery slots.</li>
<li><b>Language models can still be wrong.</b> Low temperature and strict rules reduce this; they do not remove it.</li>
</ul>
{fig("E-13")}

<h2>Who should not use it</h2>
<ul>
<li>Anyone wanting <b>health, allergy or food-safety advice</b> — ask a doctor or the label.</li>
<li>Anyone needing a <b>confirmed order, price, refund or delivery time</b> — only staff can confirm.</li>
<li>Anyone who would type <b>card numbers, passwords, one-time PINs</b> or other private details — never share these in the chat.</li>
<li><b>Real customers of any real egg business</b> — Pugad Fresh Eggs does not exist; every detail is made up.</li>
<li>Anyone using it for something that matters when it is down — there is no uptime guarantee.</li>
</ul>
"""

BODY["baseline.html"] = f"""
<p class="kicker">Section 4</p>
<h1>Baseline: the setup before we touched it</h1>
<p class="lede">On 10 November 2026 we started from a stock copy of LibreChat on a laptop and an empty AWS account.</p>

{fig("E-05", "— stock LibreChat v0.8.9-rc1, run locally by Justine")}

{table(["Area", "Baseline (10 Nov 2026)"], [
  ["Application", "Stock LibreChat v0.8.9-rc1, default name and logo, all features on (search, RAG, vector DB) " + ev("E-05")],
  ["Where it ran", "One laptop (WSL + Docker), <code>http://localhost:3080</code> — nobody else could reach it"],
  ["HTTPS", "None"],
  ["Secrets", "API key in a <code>.env</code> file on the laptop"],
  ["Shop knowledge", "None — a general chatbot that would answer anything"],
  ["Monitoring and alarms", "None"],
  ["Backups", "None"],
  ["Automation", "None — everything started by hand"],
  ["AWS account", "New Builder ID with MFA, Sydney region " + ev("E-12")],
  ["Cost", "USD 0.00 used, USD 25 budget just created " + ev("E-16")],
])}

<div class="grid-2">{fig("E-16")}{fig("E-12")}</div>
"""

BODY["well-architected.html"] = f"""
<p class="kicker">Section 5</p>
<h1>Well-Architected review</h1>
<p class="lede">AWS's six pillars, each rated against what we actually built and can show.</p>

{table(["Pillar", "Rating", "Why"], [
  ["Operational excellence", r("good"), "Dashboard, 8 alarms, written disk-full runbook used in a real drill, config in Git, two automations " + ev("E-06", "E-07", "E-12b")],
  ["Security", r("adequate"), "MFA, least-privilege IAM role, secrets in Parameter Store, HTTPS, CloudTrail, registration closed. But 80/443 open to the world (CloudFront blocked), no WAF, questions kept in request logs " + ev("E-12")],
  ["Reliability", r("gap"), "Single server in one Availability Zone with no automatic recovery. Backups are nightly (up to 24 h of data loss) and a restore was proven " + ev("E-11b") + ". The model's free-tier quota also stops answers " + ev("E-13")],
  ["Performance efficiency", r("adequate"), "Slim stack (~785 MiB). CPU and memory have headroom " + ev("E-06") + ", but answers can take ~27 s and there is a slow-answers alarm rather than a fix"],
  ["Cost optimisation", r("good"), "USD 25 budget alert, unused services switched off, 30-day log retention, old backups expire " + ev("E-16", "E-10")],
  ["Sustainability", r("adequate"), "Small footprint and nothing idle running beyond the one server; no scheduled shut-down at night"],
])}

<h2>Gap to fix first: Reliability — the single server</h2>
<div class="callout bad">
<p style="margin-top:0"><b>Problem.</b> Everything (web server, app, database) is on one EC2 instance. If it fails, customers get nothing until a person
notices, logs in and rebuilds it by hand, and the newest data is only as fresh as last night's backup.</p>
<p><b>Why first.</b> It is the only failure that takes the whole service down <em>and</em> loses data. The alarm <code>pugad-instance-unhealthy</code>
already detects it; nothing acts on it yet.</p>
<p style="margin-bottom:0"><b>Fix.</b> (1) Add the EC2 <em>recover</em> action to <code>pugad-instance-unhealthy</code> so AWS moves the instance to healthy hardware
automatically. (2) Turn on daily EBS snapshots with Data Lifecycle Manager so a whole-server rebuild takes minutes, not an afternoon.
(3) Move backups from nightly to every 6 hours to cut worst-case data loss from 24 h to 6 h. All three cost cents a month.</p>
</div>
"""

BODY["operations.html"] = f"""
<p class="kicker">Section 6</p>
<h1>Monitoring, backup &amp; restore, security</h1>

<h2 id="monitoring">Dashboard</h2>
<p>The <code>pugad-ops</code> dashboard shows, on one screen: an alarm strip, questions asked, answer time, failures (failed answers and
server errors), CPU %, memory % and disk % with the alarm lines drawn in. Memory and disk come from the CloudWatch agent; questions,
answer time and failures are pulled from the nginx request log. {ev("E-06")}</p>
{fig("E-06")}

<h2>Alarms</h2>
{table(["Alarm", "Fires when", "Why it matters"], [
  ["<code>pugad-high-cpu</code>", "CPU above 85%", "Server overloaded, answers slow"],
  ["<code>pugad-memory-pressure</code>", "Memory above 90%", "Containers may be killed"],
  ["<code>pugad-disk-filling</code>", "Disk above 85% for 5 min", "At 100% MongoDB stops writing"],
  ["<code>pugad-instance-unhealthy</code>", "EC2 status check fails", "Server itself is broken"],
  ["<code>pugad-server-errors</code>", "5xx responses in the request log", "App is failing customers"],
  ["<code>pugad-answers-failing</code>", "Chat answers failing", "Model or app problem (e.g. quota)"],
  ["<code>pugad-slow-answers</code>", "Answer time too high", "Customers waiting"],
  ["<code>pugad-backup-missing</code>", "No 'backup ok' log line in time", "Nightly backup did not run"],
  ["<code>pugad-site-down</code>", "Health check reports not OK", "Site unreachable from outside (added with the Lambda)"],
])}
<p>All alarms send email through SNS topic <code>pugad-alerts</code>. {ev("E-07")}</p>
{fig("E-07")}

<h2>The real alert</h2>
<p>During the staged disk-full fault on 14 Nov 2026 the team received a real email from <code>pugad-disk-filling</code> at
<b>15:54:06 UTC</b> with a datapoint of 87.2%. The full story is on <a href="automation.html#incident">Automation &amp; incident</a>. {ev("E-12a", "E-12b")}
We also triggered <code>pugad-high-cpu</code> with a CPU stress test and received its ALARM email. {todo("add E-08 alarm-email screenshot")}</p>

<h2 id="backup">Backup and restore</h2>
<p>Every night at 18:00 UTC (02:00 Manila), a systemd timer runs <code>scripts/backup.sh</code>: it dumps the MongoDB database and the app
config, uploads both to the private, versioned bucket <code>pugad-backups-hm123</code>, and writes "backup ok" to a log CloudWatch watches. {ev("E-11a", "E-15b")}</p>
{fig("E-11a")}

<h3>Restore test result: PASS (on the second try)</h3>
{table(["", "Attempt 1", "Attempt 2"], [
  ["Backup file", "<code>mongo-20261113T180004Z.gz</code> (10.5 KB, nightly)", "<code>mongo-20261114T160442Z.gz</code> (15.7 KB, run by hand)"],
  ["Restored on", "Laptop, throwaway <code>mongo:8</code> container", "same"],
  ["<code>mongorestore</code>", "58 restored, 0 failed", "67 restored, 0 failed"],
  ["users / convos / messages", "<b>0 / 0 / 0</b>", "<b>1 / 1 / 2</b>"],
  ["Live server at the time", "1 / 1 / 2", "1 / 1 / 2 " + ev("E-11b")],
  ["Matches live?", r("gap").replace("Gap", "No"), r("good").replace("Good", "Yes")],
])}
<div class="callout"><b>What attempt 1 taught us.</b> The first restore "worked" with zero errors but held no users or chats — the account
had been created <em>after</em> that night's backup. A restore with no errors is not proof; always compare counts with the live database.</div>
<p><b>RPO</b> (data we could lose): up to 24 hours. <b>RTO</b> (time to restore the database once the file is downloaded): about 5 minutes.
Full steps: <a href="{REPO}/blob/main/docs/restore-test.md">docs/restore-test.md</a>.</p>
{fig("E-11b")}

<h2 id="security">Security: before and after</h2>
{table(["Area", "Before", "After"], [
  ["Account sign-in", "New account", "Builder ID with MFA (TOTP) " + ev("E-12")],
  ["Secrets", "API key in a <code>.env</code> file", "5 secrets in SSM Parameter Store (encrypted), loaded into memory at start; <code>.env</code> and keys in <code>.gitignore</code>; gitleaks on the laptop"],
  ["Server permissions", "—", "<code>pugad-ec2-role</code>, least privilege: read content bucket and secrets, <em>upload-only</em> to backups"],
  ["Admin access", "—", "Session Manager from the AWS console (no SSH port open)"],
  ["Traffic", "<code>http://localhost</code>", "HTTPS only via Caddy + Let's Encrypt"],
  ["Network rules", "Design: HTTP from CloudFront only", "Now: 80/443 from anywhere (CloudFront blocked) — a known weakness"],
  ["Sign-ups", "Anyone could register", "Registration closed after the team signed up"],
  ["Storage", "—", "Both S3 buckets private, backups versioned"],
  ["Audit", "None", "CloudTrail <code>pugad-trail</code> records every AWS action"],
  ["Chatbot misuse", "General chatbot", "Answers only from documents; refuses prompt injection; never asks for card numbers " + ev("E-14")],
])}
"""

BODY["automation.html"] = f"""
<p class="kicker">Section 7</p>
<h1>Automation and the incident</h1>

<h2>Automation 1 — nightly backup</h2>
<p><b>What:</b> systemd timer <code>pugad-backup.timer</code> runs <code>pugad-backup.service</code> → <code>scripts/backup.sh</code> every day at
<code>18:00:00 UTC</code> (02:00 Manila), with <code>Persistent=true</code> so a missed run happens at next boot.</p>
<p><b>Proof it runs on its own</b> — "backup ok" lines in CloudWatch Logs: {ev("E-15b")}</p>
<ul class="timeline">
  <li><time>2026-11-11 18:00:12Z</time> 20261111T180004Z backup ok</li>
  <li><time>2026-11-12 18:00:11Z</time> 20261112T180004Z backup ok</li>
  <li><time>2026-11-13 18:00:13Z</time> 20261113T180004Z backup ok</li>
  <li><time>2026-11-14 16:04:50Z</time> 20261114T160442Z backup ok <small>(started by hand for the restore test)</small></li>
  <li><time>2026-11-14 18:00:13Z</time> 20261114T180004Z backup ok</li>
</ul>
{fig("E-15b")}

<h2>Automation 2 — health check every 15 minutes</h2>
<p><b>What:</b> Lambda <code>pugad-health-check</code>, triggered by EventBridge Scheduler <code>pugad-health-check-every-15m</code>
(<code>rate(15 minutes)</code>), calls <code>https://13-239-67-10.sslip.io/api/config</code> from outside the server and writes two metrics,
<code>HealthCheckOK</code> and <code>HealthCheckLatency</code>. Alarm <code>pugad-site-down</code> fires if it is not OK.
Code: <a href="{REPO}/blob/main/infra/health-check/lambda_function.py">infra/health-check/lambda_function.py</a>. {ev("E-09b")}</p>
<p><b>First test:</b> status 200, ok 1, latency 0.638 s. {ev("E-09")}</p>
<p><b>Proof it runs on its own</b> — consecutive runs exactly 15 minutes apart, all OK: {ev("E-15a")}</p>
<ul class="timeline">
  <li><time>2026-11-15 12:35:23Z</time> HealthCheckOK 1 · status 200</li>
  <li><time>2026-11-15 12:50:23Z</time> HealthCheckOK 1 · status 200</li>
  <li><time>2026-11-15 13:05:23Z</time> HealthCheckOK 1 · status 200</li>
  <li><time>2026-11-15 13:20:23Z</time> HealthCheckOK 1 · status 200</li>
  <li><time>2026-11-15 13:35:23Z</time> HealthCheckOK 1 · status 200</li>
  <li><time>…</time> through <time>2026-11-15 14:50:23Z</time> — 100 runs matched the query (40 shown, all OK)</li>
</ul>
<div class="grid-2">{fig("E-09")}{fig("E-09b")}</div>
{fig("E-15a")}

<h2 id="incident">The incident: disk full (staged), 14 Nov 2026</h2>
<p>We broke the server on purpose to prove the alarm, the runbook and the fix all work. All times UTC.</p>
<ul class="timeline">
  <li><time>15:40</time> Fault starts: <code>/var/log/pugad/debug.log</code> begins growing with no size limit.</li>
  <li><time>15:47</time> Disk at 73%. {ev("E-12a")}</li>
  <li><time>15:50</time> Disk at 88% — over the 85% alarm line.</li>
  <li><time>15:51</time> Peak: 93% (19 G of 20 G used).</li>
  <li><time>15:54:06</time> <b>Alarm email</b> from <code>pugad-disk-filling</code>, datapoint 87.2%.</li>
  <li><time>15:55:10</time> <b>Root cause found</b> by following the biggest folder: <code>/</code> 19G → <code>/var</code> 14G → <code>/var/log/pugad</code> 9.1G → <code>debug.log</code> 9.0G. {ev("E-12b")}</li>
  <li><time>15:55:44</time> <b>Fixed:</b> <code>rm /var/log/pugad/debug.log</code>; disk back to 48%.</li>
  <li><time>15:56</time> <b>Prevention in place:</b> logrotate rule + hourly timer, dry run clean. {ev("E-12c")}</li>
</ul>
{disk_chart()}

{table(["", ""], [
  ["Root cause", "A debug log in <code>/var/log/pugad</code> had no size limit and no rotation"],
  ["Time to detect", "~4 min after crossing 85% (the alarm uses a 5-minute average)"],
  ["Time to fix after the alarm", "~2 min"],
  ["Fix", "Deleted the runaway file; checked the site still answered"],
  ["Prevention", "<code>/etc/logrotate.d/pugad</code>: daily, <code>maxsize 100M</code>, keep 7, compress; logrotate timer changed from daily to hourly so the size check runs often"],
  ["Lesson", "On XFS, <code>fallocate</code> reserves the whole new size, so the fill had to be done in 1 GB chunks; freed space shows a few seconds after <code>rm</code>"],
])}
<div class="grid-2">{fig("E-12a")}{fig("E-12b")}</div>
{fig("E-12c")}

<h2>Runbook</h2>
<p>The step-by-step runbook we followed: <b>confirm</b> (<code>df -h /</code>) → <b>find what is big</b> (<code>du</code> from the top down) →
<b>fix</b> (delete or truncate the runaway file; restart a container if space does not come back) → <b>check the service</b> → <b>prevent</b>.
It lists the usual suspects and what is never safe to delete (the MongoDB data volume and <code>.env</code>).
Full text: <a href="{REPO}/blob/main/docs/runbook-disk-full.md">docs/runbook-disk-full.md</a>.</p>
"""

BODY["results.html"] = f"""
<p class="kicker">Section 8</p>
<h1>Results: before and after</h1>

{table(["Measure", "Before", "After", "Evidence"], [
  ["Who can use it", "Only the laptop owner (localhost)", "Anyone with the link, over HTTPS", ev("E-01", "E-15a")],
  ["Answers about the shop", "None (general chatbot)", "Correct on test set; refuses off-topic and injection", ev("E-01", "E-14")],
  ["Knowing it is up", "No checks", "Checked every 15 min from outside; 100 runs logged, every run shown returned 200", ev("E-15a")],
  ["Alarms", "0", "8 + site-down, all emailing the team", ev("E-07")],
  ["Backups", "None", "Nightly, 5 successful runs logged", ev("E-15b")],
  ["Proven restore", "No", "Yes — counts matched live (1/1/2)", ev("E-11b")],
  ["Worst-case data loss (RPO)", "Everything", "Up to 24 h", ""],
  ["Time to restore database (RTO)", "Not possible", "~5 min once downloaded", ""],
  ["Disk-full: detect / fix", "Would go unnoticed", "~4 min / ~2 min", ev("E-12b")],
  ["App memory footprint", "Full LibreChat stack", "~785 MiB slim stack", ""],
  ["Monthly AWS cost", "USD 0.00", (f"USD {sum(COST_AFTER.values()):.2f}" if all(v is not None for v in COST_AFTER.values()) else todo("fill from Cost Explorer")), ev("E-16")],
])}

<h2>Graph: the disk-full fault, before and after the fix</h2>
{disk_chart()}

<h2>Graph: restore test, before and after we fixed the method</h2>
{bar_chart("Records restored from backup (users + conversations + messages)",
           "Attempt 1 used a backup taken before the account existed. Attempt 2 used a fresh backup and matched live.",
           [("Attempt 1 (13 Nov backup)", 0, False, "0 users, 0 convos, 0 messages"),
            ("Attempt 2 (14 Nov backup)", 4, True, "1 user, 1 convo, 2 messages"),
            ("Live server", 4, False, "1 user, 1 convo, 2 messages")])}
<p style="color:var(--muted);font-size:.85rem">Source: <a href="{REPO}/blob/main/docs/restore-test.md">restore-test.md</a> {ev("E-11b")}</p>

<h2>Cost</h2>
<p><b>The whole project cost USD 0.00.</b> Every AWS service we used stayed inside the AWS Free Tier, and the Gemini model
ran on Google AI Studio's free tier. Before: USD 0.00 used against a USD 25 monthly budget on 10 Nov 2026. {ev("E-16")}
Cost controls in place: budget alert, slim stack (search, RAG and vector DB off), 30-day log retention, and the
<code>expire-old-backups</code> lifecycle rule. {ev("E-10")}</p>
{cost_block()}
"""

BODY["next-steps.html"] = f"""
<p class="kicker">Section 9</p>
<h1>Next steps, in priority order</h1>
<ol>
<li><h3>Make the single server recover itself</h3>
<p>Add the EC2 <em>recover</em> action to <code>pugad-instance-unhealthy</code>, take daily EBS snapshots with Data Lifecycle Manager,
and run backups every 6 hours instead of nightly. Closes the Reliability gap; cuts worst-case data loss from 24 h to 6 h. Cost: cents.</p></li>
<li><h3>Stop the model running out of quota</h3>
<p>Move the Gemini key to a paid tier with a spend cap, or add a second model as a fallback, so customers never see "status 429". {ev("E-13")}
Add a clear friendly message when the model is unavailable.</p></li>
<li><h3>Put CloudFront (and a firewall) back in front</h3>
<p>Once the account verification clears: CloudFront with AWS WAF, a proper domain name, and the security group closed to the CloudFront
prefix list only. Removes the open-to-the-world ports and adds caching.</p></li>
<li><h3>Keep less personal data</h3>
<p>Stop writing the request body (the customer's question) into the nginx log, or mask it, and shorten log retention for requests.
Better privacy at no cost.</p></li>
<li><h3>Automate the restore test</h3>
<p>A weekly job that restores the newest backup into a throwaway container and compares counts with live — the lesson from attempt 1 — and
alarms if they differ.</p></li>
</ol>
"""


def evidence_body():
    rows = []
    for i, (f, cap) in EV.items():
        rows.append(f'<tr><td><a href="#{i}"><b>{i}</b></a></td><td>{esc(cap)}</td></tr>')
    figs = "".join(fig(i) for i in EV)
    return f"""
<p class="kicker">Section 10</p>
<h1>Evidence register</h1>
<p class="lede">Every screenshot used on this site. Each claim on the other pages has a small tag like {ev("E-06")} next to it — click it
to open the full-size image. Personal details (emails, IPs, ARNs) are blurred or blacked out.</p>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>What it shows</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<p>Also in the repository: <a href="{REPO}/blob/main/docs/runbook-disk-full.md">runbook</a>,
<a href="{REPO}/blob/main/docs/restore-test.md">restore test</a>,
<a href="{REPO}/tree/main/infra">infra configs</a>, <a href="{REPO}/tree/main/scripts">scripts</a>,
<a href="{REPO}#contribution-log">contribution log</a>.</p>
{figs}
"""


BODY["evidence.html"] = evidence_body()

_video = (f'<div class="video"><iframe src="{esc(VIDEO_URL)}" title="Pugad Assist project video" allowfullscreen '
          f'referrerpolicy="strict-origin-when-cross-origin" '
          f'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe></div>'
          f'<p><a href="{esc(VIDEO_URL.replace("/embed/", "/watch?v="))}" target="_blank" rel="noopener">Watch on YouTube</a> '
          f'if the player does not load.</p>'
          if VIDEO_URL else
          '<div class="todo-block"><b>Video goes here.</b> Upload it to YouTube (Unlisted is fine), copy the embed link '
          '(<code>https://www.youtube.com/embed/…</code>), put it in <code>VIDEO_URL</code> in '
          '<code>scripts/build-site.py</code> and re-run the script.</div>')

BODY["declaration.html"] = f"""
<p class="kicker">Section 10</p>
<h1>Declaration and video</h1>

<h2>Video</h2>
{_video}

<h2>Declaration</h2>
<p>Signed by {esc(HARMAN_FULL_NAME)} and {esc(JUSTINE_FULL_NAME)} on {esc(DECLARATION_DATE)}. Pugad Assist is based on
LibreChat by Danny Avila and contributors (MIT licence); our individual contributions are recorded in the
<a href="{REPO}#contribution-log">contribution log</a>.</p>
<figure class="ev decl" id="DECL"><a class="img" href="evidence/declaration-signed.png" target="_blank" rel="noopener">
<img src="evidence/declaration-signed.png" alt="Signed declaration: the work is our own, the base system is credited, all data is invented, evidence is authentic, no credentials are in the repository; signed by Harman Magar and Justine Gabriel Esguerra on 16 November 2026"></a>
<figcaption><b>DECL</b> · Signed declaration (click to open full size)</figcaption></figure>
"""


# ---------------------------------------------------------------------------
# layout
# ---------------------------------------------------------------------------
NAV = [("architecture.html", "Report"), ("system-card.html", "System card"), ("results.html", "Results"),
       ("evidence.html", "Evidence"), ("declaration.html", "Video")]
APP_URL = "https://13-239-67-10.sslip.io"


def layout(fname, title, body):
    nav = "".join(f'<a href="{f}"{" aria-current=page" if f == fname else ""}>{esc(t)}</a>' for f, t in NAV)
    idx = [p[0] for p in PAGES].index(fname)
    prev_ = PAGES[idx - 1] if idx > 0 else None
    next_ = PAGES[idx + 1] if idx + 1 < len(PAGES) else None
    is_home = fname == "index.html"
    pager = ""
    if not is_home:
        pager = '<nav class="pager" aria-label="Page">'
        pager += f'<a href="{prev_[0]}"><small>Previous</small>{esc(prev_[2])}</a>' if prev_ else "<span></span>"
        pager += f'<a href="{next_[0]}" style="text-align:right"><small>Next</small>{esc(next_[2])}</a>' if next_ else ""
        pager += "</nav>"
    names = esc(HARMAN_FULL_NAME) + " and " + (esc(JUSTINE_FULL_NAME) if JUSTINE_FULL_NAME else todo("Justine — full name"))
    email = " · ".join(f'<a href="mailto:{esc(e)}">{esc(e)}</a>' for e in FOOTER_EMAILS) if FOOTER_EMAILS else todo("email")
    page_title = "Pugad Assist on AWS" if is_home else f"{title} · Pugad Assist"
    main = body if is_home else f'<div class="content">{body}{pager}</div>'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<meta name="description" content="SAM10 final project: Pugad Assist, a shop chatbot deployed and operated on AWS.">
<link rel="icon" href="assets/favicon-32x32.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="assets/site.css">
</head>
<body class="{'home' if is_home else 'inner'}">
<div class="aurora" aria-hidden="true"><span class="blade b1"></span><span class="blade b2"></span><span class="blade b3"></span><span class="blade b4"></span></div>
<div class="page">
<header class="pill-nav">
  <a class="logo" href="index.html"><span class="diamond"></span>Pugad Assist</a>
  <nav class="nav-links" aria-label="Main">{nav}</nav>
  <div class="nav-right">
    <a class="muted-link" href="{REPO}">GitHub</a>
    <a class="pill-cta" href="{APP_URL}" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg>Open app</a>
  </div>
</header>
<main>
{main}
</main>
<footer class="site-foot"><span>{names}</span><span>{email}</span></footer>
</div>
<script src="assets/site.js"></script>
</body>
</html>
"""


def write_arch_svg():
    """Standalone copy of the diagram for the home page cards (CSS variables replaced by plain dark values)."""
    svg = ARCH_SVG
    for k, v in {"var(--surface-2)": "#15161a", "var(--surface)": "#101114", "var(--line)": "rgba(255,255,255,.22)",
                 "var(--brand-ink)": "#ffb347", "var(--brand)": "#ff6b4a", "var(--ink-2)": "#c9c9ca", "var(--ink)": "#ffffff",
                 "var(--muted)": "#9c9c9d", "var(--font)": "Inter,system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif"}.items():
        svg = svg.replace(k, v)
    s0, s1 = svg.index("<style>"), svg.index("</style>") + len("</style>")
    style = svg[s0:s1]
    body = svg[s1:].strip()
    body = body.replace('<svg class="arch"', '<svg xmlns="http://www.w3.org/2000/svg" class="arch" style="background:#0b0c0f"', 1)
    body = body.replace("<defs>", "<defs>" + style, 1)
    (OUT / "assets" / "architecture.svg").write_text(body, encoding="utf-8")


def main():
    for f, _, title in PAGES:
        (OUT / f).write_text(layout(f, title, BODY[f]), encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    write_arch_svg()
    missing = [i for i, (f, _) in EV.items() if not (OUT / "evidence" / f).exists()]
    print(f"Built {len(PAGES)} pages into {OUT}")
    if missing:
        print("Missing evidence files:", ", ".join(missing))


if __name__ == "__main__":
    main()

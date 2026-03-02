#!/usr/bin/env python3
"""Watchdog: alerts via OpenClaw message tool (Telegram) if any PLAN.md task is In Progress for too long.
- Reads PLAN.md and finds tasks marked In Progress.
- If any task's 'Last updated' timestamp is older than threshold, it posts an alert to Telegram via OpenClaw message CLI.

Config via environment or defaults:
- THRESHOLD_MINUTES: integer (default 10)
- PLAN_PATH: path to PLAN.md

This script is intended to be run by OpenClaw cron every 10 minutes.
"""
import os
import re
import datetime
from pathlib import Path

PLAN_PATH = os.environ.get('PLAN_PATH') or r'C:\Users\n1sol\.openclaw\workspace\PLAN.md'
THRESH_MIN = int(os.environ.get('THRESHOLD_MINUTES') or '10')

now = datetime.datetime.now()
plan = Path(PLAN_PATH)
if not plan.exists():
    print('PLAN.md not found at', PLAN_PATH)
    raise SystemExit(1)

text = plan.read_text(encoding='utf-8')
# naive parse: find lines with '- [ ]' or '- [x]' and 'Status: In Progress'
in_progress = []
for m in re.finditer(r"- \[(.| )\] (.+?)\n\s*- .*Status: In Progress(.+?)\n", text, flags=re.S):
    task = m.group(2).strip()
    # attempt to find a timestamp later in the Task block
    block = m.group(0)
    ts_m = re.search(r"Last updated:\s*(.+)", block)
    ts = None
    if ts_m:
        try:
            ts = datetime.datetime.fromisoformat(ts_m.group(1).strip())
        except Exception:
            ts = None
    in_progress.append((task, ts))

alerts = []
for task, ts in in_progress:
    if ts is None:
        alerts.append((task, 'no timestamp'))
    else:
        delta = now - ts
        if delta.total_seconds() > THRESH_MIN * 60:
            alerts.append((task, f'{int(delta.total_seconds()/60)} minutes'))

if alerts:
    # build message
    lines = ['Watchdog Alert: long-running tasks detected:']
    for t, info in alerts:
        lines.append(f'- {t}: {info}')
    msg = '\n'.join(lines)
    # Use OpenClaw CLI (message tool) if available; fallback to printing
    try:
        import shutil
        from subprocess import run, PIPE, TimeoutExpired
        oc_path = shutil.which('openclaw')
        # allow environment override
        oc_path = oc_path or os.environ.get('OPENCLAW_CLI_PATH')
        if oc_path:
            try:
                run([oc_path,'message','send','--channel','telegram','--message',msg], check=True, timeout=600)
                print('Alert sent via openclaw')
            except TimeoutExpired:
                raise
            except Exception as e:
                raise
        else:
            raise FileNotFoundError('openclaw CLI not found on PATH')
    except Exception as e:
        # attempt direct Telegram send using token from SECRETS.md as a secondary fallback
        try:
            token = None
            sec = Path(__file__).resolve().parent.parent / 'SECRETS.md'
            if sec.exists():
                import re
                s = sec.read_text(encoding='utf-8')
                m = re.search(r'telegram_bot_token:\s*(\S+)', s)
                if m:
                    token = m.group(1).strip()
            if token:
                try:
                    import requests
                    chat_id = os.environ.get('WATCHDOG_TG_CHAT') or os.environ.get('TELEGRAM_CHAT_ID')
                    if not chat_id:
                        # if not provided, try reading last known chat id from PLAN.md (not guaranteed)
                        chat_id = None
                    payload = {'chat_id': chat_id, 'text': msg}
                    # if chat_id is None, use sendMessage with disabling_chat_id - will fail
                    r = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', json=payload, timeout=20)
                    if r.ok:
                        print('Alert sent via Telegram API')
                        # successful send; skip fallback
                    else:
                        print('Telegram send failed:', r.text)
                except Exception as e3:
                    print('Telegram send exception:', e3)
            # fallback: write to logs and append to PLAN.md so alerts are never lost
            log_dir = Path('logs') / 'watchdog'
            log_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.datetime.now().isoformat().replace(':','-')
            log_path = log_dir / f'watchdog_alert_{ts}.log'
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write('Failed to send alert via openclaw message and Telegram: ' + str(e) + '\n')
                f.write(msg + '\n')
            # append to PLAN.md
            with open(PLAN_PATH, 'a', encoding='utf-8') as pfile:
                pfile.write('\n\n# Watchdog fallback alert: ' + datetime.datetime.now().isoformat() + '\n')
                pfile.write(msg + '\n')
            print('Alert logged to', str(log_path))
        except Exception as e2:
            print('Failed to write fallback log:', e2)
            print('Original alert:', msg)
else:
    print('No stale In Progress tasks')

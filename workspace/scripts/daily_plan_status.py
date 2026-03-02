#!/usr/bin/env python3
"""Daily PLAN.md status reporter
- Reads PLAN.md and summarizes tasks by status
- Sends a short report to Telegram via OpenClaw message tool
- Intended to run once daily at 08:30 HKT (as requested previously)
"""
import os
from pathlib import Path
import re

PLAN_PATH = os.environ.get('PLAN_PATH') or r'C:\Users\n1sol\.openclaw\workspace\PLAN.md'
plan = Path(PLAN_PATH)
if not plan.exists():
    print('PLAN.md not found')
    raise SystemExit(1)

text = plan.read_text(encoding='utf-8')
# Find task lines '- [ ]' and capture status in following lines
tasks = []
for m in re.finditer(r"- \[(.| )\] (.+?)\n(\s*- .+?Status: (.+?))(?=\n- \[|\Z)", text, flags=re.S):
    name = m.group(2).strip()
    status = m.group(4).strip()
    tasks.append((name, status))

summary = {}
for name, status in tasks:
    summary.setdefault(status, []).append(name)

lines = [f'Daily PLAN.md status ({len(tasks)} tasks):']
for status, names in summary.items():
    lines.append(f'- {status}: {len(names)}')
    for n in names[:5]:
        lines.append(f'  - {n}')

msg = '\n'.join(lines)
try:
    from subprocess import run
    run(['openclaw','message','send','--channel','telegram','--message',msg], check=True)
    print('Status sent')
except Exception as e:
    print('Failed to send status via openclaw message:', e)
    print(msg)

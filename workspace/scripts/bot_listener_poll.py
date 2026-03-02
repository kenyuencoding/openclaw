#!/usr/bin/env python3
"""
Lightweight Telegram long-polling bot listener (safe, polling-based)
- Reads token from workspace SECRETS.md (telegram_bot_token: value)
- Polls getUpdates, looks for messages that mention the bot username or start with prefix 'Eon:'
- Replies to commands: help, brief now, plan, translate <text>
- Logs to logs/bot/<timestamp>.log
- Rate-limited replies (default 2/min per chat)
"""
import time, re, os, sys, json
from pathlib import Path
import requests
from datetime import datetime, timedelta

WORKSPACE = Path(__file__).resolve().parent.parent
SECRETS = WORKSPACE / 'SECRETS.md'
LOG_DIR = WORKSPACE / 'logs' / 'bot'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# read token from SECRETS.md (format: telegram_bot_token: [REDACTED] stored)
token = None
if SECRETS.exists():
    txt = SECRETS.read_text(encoding='utf-8')
    m = re.search(r'telegram_bot_token:\s*(.+)', txt)
    if m:
        token = m.group(1).strip()
# fallback: environment
if not token:
    token = os.environ.get('TELEGRAM_BOT_TOKEN')

if not token:
    print('No telegram token found; exiting')
    sys.exit(1)

API = f'https://api.telegram.org/bot{token}'

# detect bot username
resp = requests.get(f'{API}/getMe', timeout=10)
if not resp.ok:
    print('getMe failed', resp.text); sys.exit(1)
bot_info = resp.json().get('result', {})
bot_username = bot_info.get('username')
print('Bot username:', bot_username)

# state
offset = None
last_req = datetime.utcnow()
last_sent = {}  # chat_id -> [timestamps]
RATE_LIMIT = 2  # replies per minute per chat

# helpers
def log(msg):
    t = datetime.now().strftime('%Y%m%d_%H%M%S')
    p = LOG_DIR / f'{t}.log'
    with open(p, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    print(msg)

def can_send(chat_id):
    now = datetime.utcnow()
    window = now - timedelta(minutes=1)
    times = last_sent.get(chat_id, [])
    times = [ts for ts in times if ts > window]
    last_sent[chat_id] = times
    return len(times) < RATE_LIMIT

def record_send(chat_id):
    last_sent.setdefault(chat_id, []).append(datetime.utcnow())

def send_message(chat_id, text, reply_to=None):
    if not can_send(chat_id):
        log(f'Rate limit exceeded for {chat_id}, skipping send')
        return False
    data = {'chat_id': chat_id, 'text': text}
    if reply_to:
        data['reply_to_message_id'] = reply_to
    r = requests.post(f'{API}/sendMessage', data=data, timeout=15)
    if r.ok:
        record_send(chat_id)
        log(f'Sent message to {chat_id}: {text[:120]}')
        return True
    else:
        log('Failed send: ' + r.text)
        return False

# simple command handlers
def handle_command(cmd, chat_id, msg_id):
    cmd = cmd.strip()
    if cmd.lower().startswith('help'):
        send_message(chat_id, 'Commands: help, brief now, plan, translate <text>', reply_to=msg_id)
    elif cmd.lower().startswith('brief now'):
        # lightweight brief: quick market snapshot using yfinance (best-effort)
        try:
            import yfinance as yf
            tops = ['NVDA','MSFT','AAPL','AMZN','GOOG']
            parts = []
            for t in tops:
                tk = yf.Ticker(t)
                h = tk.history(period='1d')
                last = h['Close'].iloc[-1] if not h.empty else 'N/A'
                parts.append(f'{t}: {last}')
            send_message(chat_id, 'Quick brief:\n' + '\n'.join(parts), reply_to=msg_id)
        except Exception as e:
            send_message(chat_id, 'Brief failed: ' + str(e), reply_to=msg_id)
    elif cmd.lower().startswith('plan'):
        # read PLAN.md first 2000 chars
        try:
            p = WORKSPACE / 'PLAN.md'
            text = p.read_text(encoding='utf-8')
            send_message(chat_id, 'PLAN.md:\n' + (text[:1800] + ('...' if len(text) > 1800 else '')), reply_to=msg_id)
        except Exception as e:
            send_message(chat_id, 'Could not read PLAN.md: ' + str(e), reply_to=msg_id)
    elif cmd.lower().startswith('translate '):
        txt = cmd[len('translate '):].strip()
        # use simple echo as placeholder or call model if available
        # For now, echo marker
        send_message(chat_id, '(中) ' + txt, reply_to=msg_id)
    else:
        send_message(chat_id, "I didn't understand. Use 'help' to see commands.", reply_to=msg_id)

# main loop
log('Starting bot listener')
while True:
    try:
        params = {'timeout': 30}
        if offset:
            params['offset'] = offset
        r = requests.get(f'{API}/getUpdates', params=params, timeout=40)
        if not r.ok:
            log('getUpdates failed: ' + r.text)
            time.sleep(5); continue
        data = r.json()
        for upd in data.get('result', []):
            offset = upd['update_id'] + 1
            if 'message' not in upd:
                continue
            msg = upd['message']
            chat = msg['chat']
            chat_id = chat['id']
            msg_id = msg.get('message_id')
            text = msg.get('text') or ''
            from_user = msg.get('from', {}).get('username')
            # ignore messages sent by the bot itself
            if from_user and from_user.lower() == bot_username.lower():
                continue
            # check if mentioned or startswith Eon:
            if bot_username and ('@' + bot_username).lower() in text.lower() or text.strip().startswith('Eon:'):
                # extract command after mention or prefix
                # remove mention
                cmd = re.sub(r'@' + re.escape(bot_username), '', text, flags=re.I).strip()
                if cmd.startswith(':'):
                    cmd = cmd[1:].strip()
                if cmd == '':
                    cmd = 'help'
                log(f'Received command in {chat_id}: {cmd}')
                handle_command(cmd, chat_id, msg_id)
        time.sleep(0.5)
    except Exception as e:
        log('Listener exception: ' + str(e))
        time.sleep(5)

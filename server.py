"""Password-gated, anonymized-only internal pilot. No persistent application data."""
import base64
import hashlib
import hmac
import html
import json
import os
import secrets
import time
from collections import defaultdict, deque
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parent
ROLES = {
    'Einbaupartner': 'PASS_EINBAUPARTNER',
    'Außendienst': 'PASS_AUSSENDIENST',
    'Innendienst': 'PASS_INNENDIENST',
}
SECRET = os.environ.get('SESSION_SECRET', '')
MISSING = [v for v in ['SESSION_SECRET', *ROLES.values()] if len(os.environ.get(v, '')) < 16]
if MISSING:
    raise SystemExit('Fehlende/zu kurze Umgebungsvariablen (mindestens 16 Zeichen): ' + ', '.join(MISSING))
if len(SECRET) < 32:
    raise SystemExit('SESSION_SECRET muss mindestens 32 Zeichen haben.')
KEY = SECRET.encode()
SECURE = os.environ.get('COOKIE_SECURE', '1') != '0'
TTL = 8 * 3600
ATTEMPTS = defaultdict(deque)

def token_for(role):
    payload = json.dumps({'r': role, 'exp': int(time.time()) + TTL, 'nonce': secrets.token_hex(12)}, separators=(',', ':')).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip('=')
    mac = hmac.new(KEY, body.encode(), hashlib.sha256).hexdigest()
    return body + '.' + mac

def role_from_cookie(raw):
    try:
        token = next((p.split('=', 1)[1] for p in raw.split('; ') if p.startswith('maxmobil_session=')), '')
        body, mac = token.split('.', 1)
        expected = hmac.new(KEY, body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)))
        return payload['r'] if payload['exp'] >= int(time.time()) and payload['r'] in ROLES else None
    except (ValueError, KeyError, TypeError):
        return None

LOGIN = '''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RECA MAXMOBIL - Interner Test</title><style>body{margin:0;background:#f4f7f1;color:#1b291b;font:16px/1.5 system-ui,Arial}main{max-width:430px;margin:8vh auto;padding:26px;background:#fff;border-top:6px solid #76b52c;box-shadow:0 5px 30px #152b1618}h1{font-size:28px}label{display:block;margin:18px 0 6px;font-weight:700}input,select,button{box-sizing:border-box;width:100%;padding:12px;font:inherit;border:1px solid #9aab98;border-radius:4px;min-height:44px}button{background:#76b52c;font-weight:700;border:0;margin-top:22px;cursor:pointer}.warn{padding:12px;background:#fff3e1;border-left:4px solid #cb8b2d;font-size:14px}.error{color:#9d332a;font-weight:700}button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #31572d;outline-offset:2px}</style><main><h1>RECA MAXMOBIL</h1><p>Geschützter interner Smartphone-Test</p><div class="warn"><strong>Nur anonymisierte Testaufträge.</strong> Keine echten Kunden-PDFs, Fotos oder Unterschriften hochladen. Änderungen sind nicht zwischen Nutzern synchronisiert und verschwinden nach dem Neuladen.</div>{error}<form method="post" action="/login"><label for="role">Bereich</label><select name="role" id="role"><option>Einbaupartner</option><option>Außendienst</option><option>Innendienst</option></select><label for="password">Bereichspasswort</label><input type="password" id="password" name="password" autocomplete="current-password" required><button type="submit">Anmelden</button></form></main></html>'''

class Handler(BaseHTTPRequestHandler):
    server_version = 'MaxmobilPilot/1'
    def log_message(self, fmt, *args):
        # Do not log form bodies, passwords or cookies.
        print('%s - %s' % (self.address_string(), fmt % args), flush=True)

    def reply(self, code, data, ctype='text/html; charset=utf-8', cookie=None, location=None):
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store, private')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        if cookie:
            self.send_header('Set-Cookie', cookie)
        if location:
            self.send_header('Location', location)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/health':
            self.reply(200, 'ok', 'text/plain; charset=utf-8')
            return
        if path == '/logout':
            sec = '; Secure' if SECURE else ''
            self.reply(303, '', cookie='maxmobil_session=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict' + sec, location='/')
            return
        if path not in ('/', '/index.html'):
            self.reply(404, 'Nicht gefunden')
            return
        role = role_from_cookie(self.headers.get('Cookie', ''))
        if not role:
            self.reply(200, LOGIN.replace('{error}', ''))
            return
        content = (ROOT / 'index.html').read_text(encoding='utf-8')
        # JSON string literal injected into a server-only HTML template.
        encoded = json.dumps(role, ensure_ascii=False).replace('<', '\\u003c')
        content = content.replace('__SERVER_ROLE_JSON__', encoded)
        self.reply(200, content)

    def do_POST(self):
        if self.path != '/login':
            self.reply(404, 'Nicht gefunden')
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            length = -1
        if length < 1 or length > 2048:
            self.reply(400, 'Ungültige Anfrage')
            return
        ip = self.client_address[0]
        now = time.monotonic()
        q = ATTEMPTS[ip]
        while q and q[0] < now - 900:
            q.popleft()
        if len(q) >= 12:
            self.reply(429, LOGIN.replace('{error}', '<p class="error">Zu viele Versuche. Bitte später erneut versuchen.</p>'))
            return
        form = parse_qs(self.rfile.read(length).decode('utf-8', 'replace'))
        role = form.get('role', [''])[0]
        password = form.get('password', [''])[0]
        expected = os.environ.get(ROLES.get(role, ''), '')
        if role not in ROLES or not hmac.compare_digest(password.encode(), expected.encode()):
            q.append(now)
            self.reply(401, LOGIN.replace('{error}', '<p class="error">Bereich oder Passwort ungültig.</p>'))
            return
        q.clear()
        sec = '; Secure' if SECURE else ''
        self.reply(303, '', cookie='maxmobil_session=' + token_for(role) + '; Path=/; Max-Age=28800; HttpOnly; SameSite=Strict' + sec, location='/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '10000'))
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()

"""Кейс 5: Telegram-бот заявок с админ-панелью.

Бот принимает заявку (имя, контакт, услуга), складывает её в JSON-хранилище
и отправляет админу уведомление. Админ-панель - локальный веб-интерфейс:
список заявок, смена статуса, поиск, экспорт в CSV.

Зависимостей нет - только стандартная библиотека Python 3.9+.

Запуск панели:
    export ADMIN_TOKEN=change-me
    export ADMIN_PORT=8080
    python3 panel.py
"""
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
ADMIN_PORT = int(os.environ.get("ADMIN_PORT", "8080"))
LEADS_FILE = os.environ.get("LEADS_FILE", "leads.json")

STATUSES = ["new", "in_progress", "done", "rejected"]

PAGE = """<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Заявки</title>
<style>
 body{font:14px/1.5 system-ui,sans-serif;margin:0;background:#f6f7f9;color:#1c1e21}
 header{background:#fff;padding:14px 20px;border-bottom:1px solid #e3e6ea;display:flex;
   gap:16px;align-items:center;flex-wrap:wrap}
 h1{font-size:16px;margin:0}
 input,select,button{font:inherit;padding:6px 10px;border:1px solid #ccd0d5;border-radius:6px;background:#fff}
 button{cursor:pointer;background:#2b6cb0;color:#fff;border-color:#2b6cb0}
 main{padding:20px;max-width:1100px}
 table{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden}
 th,td{text-align:left;padding:9px 12px;border-bottom:1px solid #eef0f2;vertical-align:top}
 th{background:#f0f2f5;font-size:12px;text-transform:uppercase;letter-spacing:.4px;color:#5b6570}
 .st{padding:2px 8px;border-radius:99px;font-size:12px;display:inline-block}
 .new{background:#fff3cd} .in_progress{background:#cfe8ff} .done{background:#cdefd8}
 .rejected{background:#f8d7da} .empty{padding:40px;text-align:center;color:#7a8288}
</style></head><body>
<header>
 <h1>Заявки</h1>
 <input id="q" placeholder="Поиск по имени, контакту, услуге" style="min-width:260px">
 <select id="f"><option value="">Все статусы</option>__FILTER__</select>
 <button onclick="location.href='/export.csv'">Экспорт CSV</button>
 <span style="margin-left:auto;color:#7a8288" id="cnt"></span>
</header>
<main><div id="wrap"></div></main>
<script>
const q=document.getElementById('q'),f=document.getElementById('f');
const OPTS=__OPTS__;
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){
 return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function optsFor(cur){return OPTS.map(function(o){
 return '<option value="'+o+'" '+(o===cur?'selected':'')+'>'+o+'</option>';}).join('');}
function render(rows){
 const w=document.getElementById('wrap');
 document.getElementById('cnt').textContent=rows.length+' шт.';
 if(!rows.length){w.innerHTML='<div class="empty">Заявок нет</div>';return;}
 let h='<table><tr><th>Дата</th><th>Имя</th><th>Контакт</th><th>Услуга</th><th>Статус</th><th></th></tr>';
 for(const r of rows){
  h+='<tr><td>'+esc(r.created_at)+'</td><td>'+esc(r.name)+'</td><td>'+esc(r.contact)
   +'</td><td>'+esc(r.service)+'</td><td><span class="st '+esc(r.status)+'">'+esc(r.status)
   +'</span></td><td><select onchange="setst(\''+r.id+'\',this.value)">'+optsFor(r.status)
   +'</select></td></tr>';
 }
 w.innerHTML=h+'</table>';
}
async function setst(id,st){
 await fetch('/api/leads/'+id+'/status',{method:'POST',
   headers:{'Content-Type':'application/json'},body:JSON.stringify({status:st})});
 load();}
async function load(){
 const r=await fetch('/api/leads');const rows=await r.json();
 const qq=q.value.toLowerCase(),ff=f.value;
 render(rows.filter(function(x){
  return (!ff||x.status===ff)&&(!qq||JSON.stringify(x).toLowerCase().indexOf(qq)>=0);}));
}
q.addEventListener('input',load);f.addEventListener('change',load);load();
</script></body></html>"""


def load_leads():
    if not os.path.exists(LEADS_FILE):
        return []
    try:
        with open(LEADS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return []


def save_leads(leads):
    tmp = LEADS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    os.replace(tmp, LEADS_FILE)


def add_lead(name, contact, service, text="", source="web"):
    leads = load_leads()
    lead = {
        "id": int(time.time() * 1000),
        "created_at": time.strftime("%Y-%m-%d %H:%M"),
        "name": name,
        "contact": contact,
        "service": service,
        "text": text,
        "source": source,
        "status": "new",
    }
    leads.insert(0, lead)
    save_leads(leads)
    return lead


def set_status(lead_id, status):
    if status not in STATUSES:
        raise ValueError("bad status")
    leads = load_leads()
    for item in leads:
        if str(item.get("id")) == str(lead_id):
            item["status"] = status
            save_leads(leads)
            return item
    return None


class Handler(BaseHTTPRequestHandler):
    server_version = "LeadsPanel/1.0"

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        raw = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _authorized(self, token):
        if not ADMIN_TOKEN:
            return True
        return token == ADMIN_TOKEN

    def _html(self):
        opts = "".join('<option value="%s">%s</option>' % (s, s) for s in STATUSES)
        page = PAGE.replace("__FILTER__", opts)
        page = page.replace("__OPTS__", json.dumps(STATUSES, ensure_ascii=False))
        return page

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/":
            return self._send(200, self._html())
        if path == "/api/leads":
            token = query.get("token", [""])[0]
            if not self._authorized(token):
                return self._send(401, "unauthorized", "text/plain")
            return self._send(
                200, json.dumps(load_leads(), ensure_ascii=False),
                "application/json; charset=utf-8",
            )
        if path == "/export.csv":
            token = query.get("token", [""])[0]
            if not self._authorized(token):
                return self._send(401, "unauthorized", "text/plain")
            lines = ["id,created_at,name,contact,service,status"]
            for item in load_leads():
                lines.append(",".join(
                    str(item.get(k) if item.get(k) is not None else "")
                    .replace(",", ";").replace('"', "'")
                    for k in ("id", "created_at", "name", "contact", "service", "status")
                ))
            return self._send(200, "\n".join(lines), "text/csv; charset=utf-8")
        return self._send(404, "not found", "text/plain")

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(raw)
        except ValueError:
            data = {}
        token = data.get("token") or self.headers.get("X-Admin-Token", "")
        if not self._authorized(token):
            return self._send(401, "unauthorized", "text/plain")

        if parsed.path == "/api/leads":
            lead = add_lead(
                data.get("name", ""), data.get("contact", ""),
                data.get("service", ""), data.get("text", ""),
                data.get("source", "web"),
            )
            return self._send(201, json.dumps(lead, ensure_ascii=False),
                              "application/json; charset=utf-8")
        if parsed.path.startswith("/api/leads/") and parsed.path.endswith("/status"):
            lead_id = parsed.path.split("/")[3]
            try:
                item = set_status(lead_id, data.get("status", ""))
            except ValueError:
                return self._send(400, "bad status", "text/plain")
            if item is None:
                return self._send(404, "not found", "text/plain")
            return self._send(200, json.dumps(item, ensure_ascii=False),
                              "application/json; charset=utf-8")
        return self._send(404, "not found", "text/plain")

    def log_message(self, fmt, *args):
        print("[panel]", fmt % args)


def run():
    if not ADMIN_TOKEN:
        print("ВНИМАНИЕ: ADMIN_TOKEN не задан - панель открыта без пароля.")
    print("Панель заявок: http://0.0.0.0:%d  (файл: %s)" % (ADMIN_PORT, LEADS_FILE))
    ThreadingHTTPServer(("0.0.0.0", ADMIN_PORT), Handler).serve_forever()


if __name__ == "__main__":
    run()

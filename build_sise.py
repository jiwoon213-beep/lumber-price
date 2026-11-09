#!/usr/bin/env python3
"""sise.html 안에 오늘 시세를 정적 HTML로 미리 넣는다 (검색엔진은 자바스크립트를 잘 안 읽기 때문).
data.json / shop.json 이 바뀐 뒤 `python3 build_sise.py` 로 실행. 페이지 자바스크립트가 같은 값으로 다시 그린다."""
import json, math, re, html, datetime, pathlib

ROOT = pathlib.Path(__file__).parent
D = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
S = json.loads((ROOT / "shop.json").read_text(encoding="utf-8"))

def vat_ex(x):
    return "VAT별도" in (x.get("m") or "")

last = {}
for x in D["prices"]:
    k = (x["s"], x["p"], x["d"]); c = last.get(k)
    if not c or x.get("t", 0) > c.get("t", 0):
        last[k] = x
dates = sorted({x["d"] for x in D["prices"]})

def min_upto(upto):
    import datetime as _dt
    lim = (_dt.date.fromisoformat(upto) - _dt.timedelta(days=30)).isoformat()
    per = {}
    for x in last.values():
        if x["d"] > upto or x["d"] < lim:
            continue
        k = (x["s"], x["p"]); c = per.get(k)
        if not c or x["d"] > c["d"]:
            per[k] = x
    out = {}
    for x in per.values():
        v = x["v"] * 1.1 if vat_ex(x) else x["v"]
        if x["p"] not in out or v < out[x["p"]]:
            out[x["p"]] = v
    return out

_cache = {}
def latest_min(pid, upto=None):
    u = upto or dates[-1]
    if u not in _cache:
        _cache[u] = min_upto(u)
    return _cache[u].get(pid)

def my_price(pid, mn):
    fx = (S.get("fixed") or {}).get(pid)
    if fx is not None:
        return fx
    if mn is None:
        return None
    r = S.get("round", 100)
    return math.ceil(mn * (1 + S.get("markup", 0) / 100) / r) * r

prev = dates[-2] if len(dates) > 1 else None
P = {p["id"]: p for p in D["products"]}

# ── 오늘의 품목: 날짜가 바뀌면 자동으로 다른 품목으로 교체 ──
import random, collections
upd0 = D.get("updated") or dates[-1]
if S.get("today_date") != upd0 or not S.get("today"):
    shops_per = collections.defaultdict(set)
    for x in last.values():
        shops_per[x["p"]].add(x["s"])
    prev_today = set(S.get("today") or []) | set(S.get("today_prev") or [])
    cand = [p for p in D["products"] if len(shops_per[p["id"]]) >= 3
            and p["id"] not in S["items"] and latest_min(p["id"]) is not None]
    fresh = [p for p in cand if p["id"] not in prev_today] or cand
    rnd = random.Random(upd0)
    rnd.shuffle(fresh)
    bycat = collections.OrderedDict()
    for p in fresh:
        bycat.setdefault(p["cat"], []).append(p)
    pick = []
    n = int(S.get("today_count", 8))
    while len(pick) < n and any(bycat.values()):
        for c in list(bycat):
            if bycat[c] and len(pick) < n:
                pick.append(bycat[c].pop(0)["id"])
    S["today_prev"] = S.get("today") or []
    S["today"] = pick
    S["today_date"] = upd0
    (ROOT / "shop.json").write_text(json.dumps(S, ensure_ascii=False, indent=2), encoding="utf-8")

TODAY_G = "오늘의 품목 · 매일 바뀝니다"
rows = []
for pid in list(S["items"]) + [x for x in (S.get("today") or []) if x not in S["items"]]:
    p = P.get(pid)
    if not p:
        continue
    v = my_price(pid, latest_min(pid))
    if v is None:
        continue
    pv = my_price(pid, latest_min(pid, prev)) if prev else None
    rows.append((p, v, (v - pv) if pv is not None else 0, TODAY_G if pid in (S.get("today") or []) else p["cat"]))

esc = html.escape
won = lambda n: f"{int(round(n)):,}"
groups = []
for p, v, df, gname in rows:
    g = next((g for g in groups if g[0] == gname), None)
    if not g:
        g = (gname, []); groups.append(g)
    g[1].append((p, v, df))
out = []
for cat, items in groups:
    out.append(f'<section class="grp"><h2>{esc(cat)}</h2>')
    for p, v, df in items:
        chg = f'<span class="chg {"up" if df > 0 else "down"}">{"▲" if df > 0 else "▼"}{won(abs(df))}</span>' if df else ""
        out.append(f'<div class="it"><div class="nm"><b>{esc(p["name"])}</b><small>{esc(p.get("spec") or "")}</small></div>'
                   f'<div class="pr"><b>{won(v)}</b>원{chg}<small>1{esc(p.get("unit") or "개")}</small></div></div>')
    out.append("</section>")
static = "".join(out)

upd = D.get("updated") or dates[-1]
y, m, d = map(int, upd.split("-"))
wd = "월화수목금토일"[datetime.date(y, m, d).weekday()]
date_txt = f"{y}년 {m}월 {d}일 ({wd}) 기준"
top = ", ".join(f'{p["name"]} {won(v)}원' for p, v, _, _ in rows[:4])

h = (ROOT / "sise.html").read_text(encoding="utf-8")
h = re.sub(r'<div id="list">.*?</div><!--/list-->|<div id="list"></div>', f'<div id="list">{static}</div><!--/list-->', h, count=1, flags=re.S)
h = re.sub(r'(<span class="date" id="date">).*?(</span>)', rf'\g<1>{date_txt}\g<2>', h, count=1)
h = re.sub(r'<title>.*?</title>', f'<title>대전 목재 시세 {m}월 {d}일 | 합판·구조목·자작합판 가격 — {esc(S["name"])}</title>', h, count=1)
h = re.sub(r'<meta name="description" content="[^"]*">',
           f'<meta name="description" content="대전·세종 목재 시세 {m}월 {d}일 기준: {esc(top)} 등. 원하는 치수로 재단, 대전·세종 배송. {esc(S["name"])}.">', h, count=1)
(ROOT / "sise.html").write_text(h, encoding="utf-8")
print(date_txt, len(rows), "품목")

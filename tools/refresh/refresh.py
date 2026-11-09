"""쇼핑몰 하나의 새 전체 상품 목록(name|price 줄)으로 data.json을 갱신한다.

사용: python3 tools/refresh/refresh.py <shop_id> <목록파일> [YYYY-MM-DD]
- data.json의 다른 날짜 가격·다른 쇼핑몰 데이터는 건드리지 않는다(CLAUDE.md 규칙).
- 그 쇼핑몰의 비교 품목 가격: 이전에 연결된 상품명과 같은 상품을 새 목록에서 찾아 오늘 날짜로 추가.
- 그 쇼핑몰의 전체 상품(catalog): 새 목록으로 교체.
"""
import json, re, sys, datetime, collections, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, 'data.json')


def clean(n, sp=''):
    """수집 때와 같은 방식으로 상품명 정리 (add_interior + merge 규칙)."""
    m = re.search(r'\s*제조사\s*:\s*(.*?)(?:\s*규격\s*:\s*(.*))?$', n)
    if m:
        n0 = n[:m.start()].strip(); mk = m.group(1).strip()
        if mk and mk != '-' and mk not in n0: n0 = f'[{mk}] ' + n0
        if m.group(2) and not sp: sp = m.group(2).strip()
        n = n0
    n = re.sub(r'\s+', ' ', n).strip()
    return n, sp


def key(s):
    s = re.sub(r'\s*제조사\s*:.*?(?=규격\s*:|$)', ' ', s)
    s = re.sub(r'규격\s*:', ' ', s)
    s = re.sub(r'\[[^\]]*\]', ' ', s)
    s = s.lower().replace('×', 'x').replace('*', 'x')
    nums = tuple(sorted(re.findall(r'\d+(?:\.\d+)?', s.replace(',', ''))))
    letters = re.sub(r'mm|[^가-힣a-z]', '', s)
    letters = re.sub(r'(?<=[^a-z])x|x(?=[^a-z])|^x|x$', '', letters)
    return letters, nums


def strip_pre(m):
    return re.sub(r'^(VAT별도 · )?(추정 · )?', '', m)


def main():
    sid, fn = sys.argv[1], sys.argv[2]
    today = sys.argv[3] if len(sys.argv) > 3 else datetime.date.today().isoformat()
    D = json.load(open(PATH, encoding='utf-8'))
    raw = []
    for line in open(fn, encoding='utf-8'):
        p = line.rstrip('\n').split('|')
        if len(p) < 2 or not p[-1].isdigit(): continue
        raw.append((p[0], p[1] if len(p) == 3 else '', int(p[-1])))
    if len(raw) < 20:
        print('목록이 너무 적음(', len(raw), ') — 수집 실패로 보고 중단'); return

    old_cat = [c for c in D['catalog'] if c['s'] == sid]
    vat = collections.Counter(c['vat'] for c in old_cat).most_common(1)[0][0] if old_cat else False
    sp_nv = {(c['n'], c['v']): c['sp'] for c in old_cat}
    names = {c['n'] for c in old_cat}

    # 새 목록 인덱스
    idx = collections.defaultdict(set)
    for n, sp, v in raw:
        n2, sp2 = clean(n, sp)
        for k in {key(n), key(n2 + ' ' + sp2), key(n2)}:
            idx[k].add(v)

    # 쇼핑몰별 최신 가격 기록
    last, ref = {}, {}   # last: 가장 최근 기록, ref: 상품명이 전체상품에 있는 가장 최근 기록(이름 연결용)
    for p in D['prices']:
        if p['s'] != sid: continue
        k = (p['s'], p['p'])
        if k not in last or p['t'] > last[k]['t']: last[k] = p
        if strip_pre(p['m']) in names and (k not in ref or p['t'] > ref[k]['t']): ref[k] = p
    maxt = max(x['t'] for x in D['prices'])
    have_today = {(p['s'], p['p']) for p in D['prices'] if p['d'] == today}
    add, miss, odd, x11 = [], 0, 0, 0
    for (s, pid), p in ref.items():
        if (s, pid) in have_today: continue
        n = strip_pre(p['m']); sp = sp_nv.get((n, p['v']), '')
        vals = None
        for k in (key(n + ' ' + sp), key(n)):
            if k in idx and len(idx[k]) == 1:
                vals = idx[k]; break
            if k in idx and len(idx[k]) > 1 and p['v'] in idx[k]:
                vals = {p['v']}; break
        if not vals: miss += 1; continue
        v = next(iter(vals))
        pv = last[(s, pid)]['v']
        # 목록가(VAT별도)와 상세가(VAT포함, 목록가x1.1)가 섞여 수집돼 있어서, 원래 기록과 같은 기준을 고른다
        v11 = int(round(v * 1.1, -1))
        if abs(v11 - p['v']) < abs(v - p['v']): v = v11; x11 += 1
        if not (pv / 2.5 <= v <= pv * 2.5): odd += 1; continue
        maxt += 1
        add.append(dict(s=s, p=pid, v=v, d=today, m=p['m'], t=maxt))
    D['prices'] += add

    # catalog 교체
    new_cat = []
    seen = set()
    for n, sp, v in raw:
        n2, sp2 = clean(n, sp)
        if not sp2:
            n3 = re.sub(r'(\d)\s*T\s*[xX×*]', r'\1 x', n2); n3 = re.sub(r'(\d)\s*X\s*(\d)', r'\1 x \2', n3)
            m = re.search(r'(\d+(?:\.\d+)?)\s*[*x×]\s*(\d+(?:\.\d+)?)(?:\s*[*x×]\s*(\d+(?:\.\d+)?))?', n3)
            if m: sp2 = 'x'.join(g for g in m.groups() if g) + 'mm'; n2 = (n3[:m.start()] + n3[m.end():]).replace('  ', ' ').strip()
        if (n2, sp2, v) in seen or v < 100: continue
        seen.add((n2, sp2, v))
        new_cat.append(dict(s=sid, n=n2, sp=sp2, v=v, vat=vat or x11 > len(add) / 2))
    D['catalog'] = [c for c in D['catalog'] if c['s'] != sid] + new_cat
    if today > D.get('updated', ''): D['updated'] = today
    json.dump(D, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    ch = sum(1 for a in add if a['v'] != last[(a['s'], a['p'])]['v'])
    miss += len(last) - len(ref)
    print(f'{sid}: 비교품목 가격 {len(add)}건 갱신(바뀜 {ch}건), 못찾음 {miss}, 이상값 제외 {odd} / 전체상품 {len(old_cat)}→{len(new_cat)}')


if __name__ == '__main__':
    main()

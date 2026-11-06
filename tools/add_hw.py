import json,re
from statistics import median
PATH='/home/claude/price-tracker/data.json'
D=json.load(open(PATH))
# (product name prefix, cat, unit, include, exclude, key-extractor regex (group1..), min shops)
F=[
('타카핀','부자재','통',r'타카\s?핀',r'스텐|SUS|스테인|타정기|해머|건\b|네일건|코일',r'타카\s?핀\s*(F\s?\d{2}|DT\s?\d{2}|ST\s?\d{2}|T\s?\d{2}|\d{3,4})J?',2),
('석고피스','부자재','봉',r'석고\s?피스',r'^$',r'(\d)\s*[xX×]\s*(\d{2})',2),
('직결 윙피스','부자재','봉',r'직결.*피스|윙\s?스크류',r'와샤|접시',r'(\d{2})\s*mm',2),
('아연 델타피스','부자재','봉',r'델타\s?피스',r'육각|메가',r'(\d{2})\s*mm',2),
('우레탄폼 (일반)','부자재','개',r'우레탄\s?폼',r'건|클리너|세척|스프레이',r'(우레탄)',2),
('실리콘','부자재','개',r'실리콘',r'건|본드|사이딩|전용|박스|25EA|\d+EA|바이오|변성|우레탄',r'(투명|반투명|백색|흰색)',2),
('세라믹사이딩 아이큐브','외장재','장',r'아이큐브 세라믹사이딩',r'부자재|스타터|실리콘|코너',r'(FUGE|N16|V16|PREMIUM|COOL)',1),
('세라믹사이딩 KMEW','외장재','장',r'KMEW|케이뮤',r'부자재|코너|실리콘',r'\]\s*(\S+)',1),
('메탈사이딩 J-Metal','외장재','M',r'J-Metal',r'부자재|코너|후레싱|몰딩',r'(스냅락|에코락|제네스)',1),
('메탈사이딩 IMS','외장재','장',r'IMS|아이엠사이딩',r'부자재|코너',r'(IMS-\d+)',1),
('시멘트사이딩 6.5x230 3.6m','외장재','장',r'시멘트\s?사이딩',r'가위|거치대|게이지|절단|5매',r'(6\.5\s*[xX*]\s*230)',1),
('아스팔트슁글 오웬스코닝','외장재','번들',r'오웬스코닝',r'부자재|못|본드|릿지|스타터',r'오웬스코닝\]?\s*(\S+)',1),
('투습방수지','외장재','롤',r'투습\s?방수|하우스랩|타이벡',r'테이프|씰|부자재',r'(JH-VENT|VAXO|DELTA|VENT [NS]|TYWRAP|타이랩|타이벡|Tyvek)',1),
]
nid=max(int(p['id'][1:]) for p in D['products']); maxt=max(x['t'] for x in D['prices'])
made=[]
for name,cat,unit,inc,exc,key,mins in F:
    g={}
    for c in D['catalog']:
        n=c['n']
        if not re.search(inc,n) or re.search(exc,n): continue
        m=re.search(key,n+' '+(c['sp'] or ''))
        if not m: continue
        k=' '.join(x for x in m.groups() if x).replace(' ','')
        k=re.sub(r'^(\d)(\d{2})$',r'\1x\2',k) if name=='석고피스' else k
        if name.startswith(('직결','아연')): k=k+'mm'
        g.setdefault(k,{})
        if c['s'] not in g[k] or c['v']<g[k][c['s']]['v']: g[k][c['s']]=c
    for k,best in sorted(g.items()):
        if len(best)>=2:
            vs=sorted(c['v'] for c in best.values()); med=vs[len(vs)//2]
            best={s:c for s,c in best.items() if med/2.2<=c['v']<=med*2.2}
        if len(best)<mins: continue
        nid+=1; pid='p%02d'%nid
        sp='' if k in('우레탄',) else k
        D['products'].append(dict(id=pid,name=name if k=='우레탄' else f'{name} {k}',spec='',unit=unit,cat=cat,key=False))
        for s,c in best.items():
            maxt+=1; D['prices'].append(dict(s=s,p=pid,v=c['v'],d=D['updated'],m=(('VAT별도 · ' if c['vat'] else '')+c['n']).strip(),t=maxt))
        made.append((pid,name,k,{s:c['v'] for s,c in best.items()}))
json.dump(D,open(PATH,'w'),ensure_ascii=False,separators=(',',':'))
for x in made: print(*x)
print(len(made),'products; total',len(D['products']),len(D['prices']))

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
('세라믹사이딩 아이큐브','외장재','장',r'아이큐브.*(세라믹사이딩|외장패널)',r'부자재|스타터|실리콘|코너|세트',r'(FUGE|N16|V16|PREMIUM|COOL|퓨제|쿨)',1),
('세라믹사이딩 KMEW','외장재','장',r'KMEW|케이뮤',r'부자재|코너|실리콘',r'\]\s*(\S+)',1),
('메탈사이딩 J-Metal','외장재','M',r'J-Metal',r'부자재|코너|후레싱|몰딩',r'(스냅락|에코락|제네스)',1),
('메탈사이딩 IMS','외장재','장',r'IMS|아이엠사이딩',r'부자재|코너',r'(IMS-\d+)',1),
('시멘트사이딩','외장재','장',r'시멘트?\s?사이딩',r'가위|거치대|게이지|절단|5매',r"(6\.5)T?\s*[xX*]\s*(230)",1),
('아스팔트슁글 오웬스코닝','외장재','번들',r'오웬스코닝',r'부자재|못|본드|릿지|스타터',r'(클래식|사각|오크리지|이중|오크유로)',1),
('매거진피스','부자재','박스',r'매거진\s?피스|자동연결피스',r'백색|연발|2000발',r'(25|32|38)\s*mm|X\s*(25|32|38)',2),
('아연피스','부자재','봉',r'아연\s?피스',r'델타|육각',r'(?:x|X)\s*(\d{2})\s*mm|^아연피스\s*(\d{2})MM',2),
('에이지엠 에코 롤슁글','외장재','롤',r'에코\s?롤\s?슁글|에코롤슁글',r'접착|스페니쉬',r'(에코)',2),
('투습방수지','외장재','롤',r'유로벤트|프로클리마|Pro Clima',r'테이프|캡|Kaflex|Roflex|접착|헤라|롤러|브러쉬|웰다노 (INCAV|invex|전용)|씰',r'(월\s?프로텍트3|맥시|(?<!프로)클리마X|(?<!프로)클리마|메탈릭|스탠다드\s?알루|파사드|Solitex Power|Mento\s?3000|Intello Plus|Intello|DA)',2),
('타이벡','외장재','롤',r'타이벡|드레인랩|에너코',r'국산|한스펙|테이프|씰|타이씰',r'(드레인랩|에너코\s?R4|에어가드|수프로|하우스랩)',2),
('투습방수지B','외장재','롤',r'투습\s?방수|하우스랩|타이벡',r'테이프|씰|부자재|국산|한스펙|타이벡|듀폰',r'(JH-VENT|VAXO|DELTA|VENT [NS]|TYWRAP|타이랩)',1),
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
        k={'퓨제':'FUGE','쿨':'COOL','사각':'클래식','이중':'오크리지'}.get(k,k)
        k=re.sub(r'^(\d)(\d{2})$',r'\1x\2',k) if name=='석고피스' else k
        if name.startswith(('직결','아연','매거진')): k=k+'mm'
        if name=='투습방수지': k=re.sub(r'\s','',k).replace('Plus','플러스')
        k='6.5x230 3.6m' if name.startswith('시멘트') else k
        g.setdefault(k,{})
        if c['s'] not in g[k] or c['v']<g[k][c['s']]['v']: g[k][c['s']]=c
    for k,best in sorted(g.items()):
        if len(best)>=2:
            vs=sorted(c['v'] for c in best.values()); med=vs[len(vs)//2]
            best={s:c for s,c in best.items() if med/2.2<=c['v']<=med*2.2}
        if len(best)<mins: continue
        nid+=1; pid='p%02d'%nid
        sp='' if k in('우레탄',) else k
        D['products'].append(dict(id=pid,name=name if k in('우레탄','에코') else f"{name.rstrip('B')} {k}",spec='',unit=unit,cat=cat,key=False))
        for s,c in best.items():
            maxt+=1; D['prices'].append(dict(s=s,p=pid,v=c['v'],d=D['updated'],m=(('VAT별도 · ' if c['vat'] else '')+c['n']).strip(),t=maxt))
        made.append((pid,name,k,{s:c['v'] for s,c in best.items()}))
json.dump(D,open(PATH,'w'),ensure_ascii=False,separators=(',',':'))
for x in made: print(*x)
print(len(made),'products; total',len(D['products']),len(D['prices']))

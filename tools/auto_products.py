import json,re
from collections import defaultdict
PATH='/home/claude/price-tracker/data.json'
D=json.load(open(PATH))
STD=[2.7,3,4,4.8,6,7.5,9,9.5,12,12.5,15,18,20,21,24,25,30,33,38]
def tb(t):
    alias={4.5:4.8,4.6:4.8,6.5:6,8.5:9,11.5:12,11:12,14.5:15,17.5:18,18.3:18,11.1:11.1}
    if t in alias: return alias[t]
    return min(STD,key=lambda s:abs(s-t)) if min(abs(s-t) for s in STD)<=0.6 else None
def dims(c):
    s=c['sp'] or ''
    d=[float(x) for x in re.findall(r'\d+(?:\.\d+)?',s)]
    if not d:
        m=re.search(r'(\d+(?:\.\d+)?)\s*T',c['n'])
        if m: d=[float(m.group(1))]
    return d
BUNDLE=r'단/|/단|한단|1단|묶음|EA|매/단|入|\d+개|번들'
GEN_X=r'계단|손스침|핸드레일|대봉|소봉|동자|후로링|무늬목|UV|코팅|템바|타공|컬러|방염|고비중|고밀도|랩핑|오버레이|양면하도|흡음'
# (name, cat, unit, include, exclude, kind)
F=[
('라디에타파인 집성판','집성판','장',r'라디에타|뉴송.*집성|칠레파인|브라질파인|피누스',r'각재|계단'),
('멀바우 집성판','집성판','장',r'멀바우',r'각재'),
('히노끼 집성판','집성판','장',r'(히노끼|편백).*집성',r'유절|각재'),
('고무나무 집성판','집성판','장',r'고무나무.*(집성|판)|고무나무\d',r'합판|각재'),
('아카시아 집성판','집성판','장',r'아카시아.*집성',r'무절|각재'),
('라왕 집성판','집성판','장',r'라왕.*(집성판|핑거집성|솔리드집성|집성목)|라왕\(나왕\) 솔리드',r'각재|합판'),
('삼나무 집성판','집성판','장',r'삼나무.*(집성|솔리드)|삼목(집성|솔리드)',r'각재'),
('레드파인 집성판','집성판','장',r'레드파인.*(집성|솔리드)',r'각재|루바'),
('오크 집성판','집성판','장',r'(오크).*집성',r'각재|레드오크|광폭'),
('애쉬 집성판','집성판','장',r'(애쉬|에쉬).*집성',r'각재|탄화|광폭'),
('스프러스 집성판','집성판','장',r'스프러스.*(집성|솔리드)',r'각재'),
('코아합판','합판','장',r'코아|코어',r'^$'),
('태고합판','합판','장',r'태고',r'^$'),
('MDF','MDF','장',r'^MDF|MDF\(레귤러\)|^\[KCC\] MDF|^MDF ',r'고밀도|고비중|템바|UV|uv|컬러|랩핑|오버레이|방염|10자|9자'),
('CRC보드','보드','장',r'CRC',r'마감캡|노출|내부|마감용'),
('방균석고보드','석고보드','장',r'방균\s?석고',r'^$'),
]
L=[ # lumber families: name,cat,unit(단=bundle),include,exclude
('삼목루바','루바','단',r'삼목.*루바|삼목\(삼나무\)루바',r'코팅|UV|찬넬|무골'),
('향목루바','루바','단',r'향목.*루바',r'코팅|UV'),
('레드파인 루바','루바','단',r'레드파인.*루바|레드파인12\*',r'무절|마감|걸레'),
('스프러스 루바','루바','단',r'스프러스.*루바',r'사이딩'),
('히노끼 유절루바','루바','단',r'히노끼.*루바|히노끼루바',r'무절|마감'),
('라왕 각재','각재','개',r'라왕.*(각재|다루끼)',r'후지|심재|집성판'),
('뉴송 투바이','각재','개',r'뉴송.*투바이|건설용 투바이',r'^$'),
('뉴송 오비끼','각재','개',r'오비끼|산승각',r'^$'),
('LVL 다루끼','각재','단',r'LVL.*다루끼',r'^$'),
('LVL 투바이','각재','단',r'LVL.*투바이',r'^$'),
('방부각재','방부목','개',r'방부',r'데크|크로바|라티스|레티스|래티스|라틱스|캡|레인|찬넬|사이딩|원주|화분|U캡|골O'),
('마감재 판재','구조목','개',r'골만|스프러스 판재|스프러스 마감재|마감재 1x|^구조목 1x',r'히노끼'),
('적삼목 판재','구조목','개',r'적삼목',r'루바'),
('히노끼 판재','구조목','개',r'히노끼.*(판재|마감재)',r'루바|무절|몰딩'),
]
P=D['products']
def pkey_sheet(p):
    m=re.match(r'([\d.]+)T',p['spec']); return float(m.group(1)) if m else None
def pkey_lum(p):
    s=p['spec']; a=[]
    for tok in re.findall(r'\d+(?:\.\d+)?m(?![m\d])|\d+(?:\.\d+)?',s):
        a.append(round(float(tok[:-1])*1000) if tok.endswith('m') else float(tok))
    return tuple(a[:3])
exist_sheet={(p['name'].split('(')[0].strip(),tb(pkey_sheet(p)) if pkey_sheet(p) else None) for p in P}
exist_lum={(p['name'].split()[0][:2],)+tuple(round(x) for x in pkey_lum(p)) for p in P if p['cat'] in('방부목','각재','구조목','루바')}
nid=max(int(p['id'][1:]) for p in P)
new_p=[];new_pr=[]
maxt=max(x['t'] for x in D['prices'])
shopname={s['id']:s['name'] for s in D['shops']}
def add(name,cat,unit,spec,members,keyflag=False):
    global nid,maxt
    best={}
    for c in members:
        if c['s'] not in best or c['v']<best[c['s']]['v']: best[c['s']]=c
    vs=sorted(c['v'] for c in best.values()); med=vs[len(vs)//2]
    best={s:c for s,c in best.items() if med/2.5<=c['v']<=med*2.5}
    if len(best)<2: return
    nid+=1; pid='p%02d'%nid
    new_p.append(dict(id=pid,name=name,spec=spec,unit=unit,cat=cat,key=keyflag))
    for s,c in best.items():
        maxt+=1
        new_pr.append(dict(s=s,p=pid,v=c['v'],d=D['updated'],m=(('VAT별도 · ' if c['vat'] else '')+c['n']).strip(),t=maxt))
for name,cat,unit,inc,exc in F:
    g=defaultdict(list)
    for c in D['catalog']:
        if not re.search(inc,c['n']) or re.search(exc,c['n']) or (cat!='MDF' and re.search(GEN_X,c['n'])): continue
        if re.search(BUNDLE,c['n']) and 'EA' not in c['n']: continue
        d=dims(c)
        if not d: continue
        if len(d)>=3:
            w,l=sorted(d[1:3])
            if cat=='석고보드':
                if not(880<=w<=920 and 1790<=l<=1830): continue
            elif not(1200<=w<=1240 and 2400<=l<=2460): continue
        elif cat=='석고보드': continue
        t=tb(d[0])
        if t is None: continue
        g[t].append(c)
    for t,mem in sorted(g.items()):
        base=name.split('(')[0].strip()
        if (base,t) in exist_sheet: continue
        spec=(f'{t:g}T 900x1800' if cat=='석고보드' else f'{t:g}T 1220x2440')
        add(name,cat,unit,spec,mem)
for name,cat,unit,inc,exc in L:
    g=defaultdict(list)
    for c in D['catalog']:
        if not re.search(inc,c['n']) or re.search(exc,c['n']) or re.search(GEN_X,c['n']): continue
        b=bool(re.search(BUNDLE,c['n']))
        if b!=(unit=='단'): continue
        d=dims(c)
        if len(d)<3: continue
        t,w=sorted(d[:2]); L_=d[2]
        if L_<1800: continue
        k=(round(t),round(w),round(L_/100)*100)
        k=next((e for e in g if abs(e[0]-k[0])<=1.5 and abs(e[1]-k[1])<=2 and e[2]==k[2]),k)
        g[k].append(c)
    for k,mem in sorted(g.items()):
        # merge near-identical sizes (e.g. 38x184 vs 38x185)
        pre=name.split()[0][:2]
        if any(e[0]==pre and len(e)>3 and abs(k[0]-e[1])<=1.5 and abs(k[1]-e[2])<=2 and abs(k[2]-e[3])<=50 for e in exist_lum): continue
        exist_lum.add((pre,)+k)
        spec=f'{k[0]}x{k[1]} {k[2]/1000:g}m'+(' (단)' if unit=='단' else '')
        add(name,cat,unit,spec,mem)
D['products']+=new_p; D['prices']+=new_pr
json.dump(D,open(PATH,'w'),ensure_ascii=False,separators=(',',':'))
from collections import Counter
print('new products',len(new_p),'prices',len(new_pr),Counter(p['cat'] for p in new_p))
for p in new_p:
    ps=[x for x in new_pr if x['p']==p['id']]
    print(p['id'],p['name'],p['spec'],len(ps),'|',' ; '.join(f"{shopname[x['s']]} {x['v']} ({x['m'][:30]})" for x in ps)[:260])

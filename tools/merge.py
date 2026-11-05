import json,re
D=json.load(open('/home/claude/price-tracker/data.json'))
SH={'daelim.txt':('o01',''),'woodnhome.txt':('o03','VAT별도 · 추정 · '),'baro09.txt':('o11','VAT별도 · '),'hanaro.txt':('o21',''),'diwood.txt':('o15',''),'hswooda.txt':('o08',''),'limwood.txt':('o09','VAT별도 · '),'woodtek.txt':('o17',''),'bds1.txt':('o16',''),'namugongjang.txt':('o22',''),'nosdom.txt':('o04','VAT별도 · '),'taeyoung.txt':('o14',''),'2x4.txt':('o05',''),'buildhousing.txt':('o10',''),'acewood.txt':('o02','VAT별도 · '),'namumok.txt':('o18','VAT별도 · '),'ssakda.txt':('o07',''),'kcc.txt':('o12','')}
cat=[]
for f,(sid,pre) in SH.items():
    for line in open(f,encoding='utf-8'):
        line=line.strip()
        if not line: continue
        parts=line.split('|')
        if len(parts)==2: n,v=parts; sp=''
        else: n,sp,v=parts[0],parts[1],parts[2]
        if not sp:
            n=re.sub(r'(\d)\s*T\s*[xX×*]',r'\1 x',n); n=re.sub(r'(\d)\s*X\s*(\d)',r'\1 x \2',n)
            m=re.search(r'(\d+(?:\.\d+)?)\s*[*x×]\s*(\d+(?:\.\d+)?)(?:\s*[*x×]\s*(\d+(?:\.\d+)?))?',n)
            if m: sp='x'.join(g for g in m.groups() if g)+'mm'; n=(n[:m.start()]+n[m.end():]).replace('  ',' ').strip()
        cat.append(dict(s=sid,n=n,sp=sp,v=int(v),pre=pre))
nums=lambda s:[float(x) for x in re.findall(r'\d+(?:\.\d+)?',s.replace(',',''))]
def pdims(p):
    s=p['spec']; s=re.sub(r'\(([\d.]+)T\)','',s)
    a=[]
    for tok in re.findall(r'\d+(?:\.\d+)?m(?![m\d])|\d+(?:\.\d+)?',s):
        if tok.endswith('m'): a.append(float(tok[:-1])*1000)
        else: a.append(float(tok))
    # drop trailing counts like (12개) and 자 length labels
    s2=p['spec']
    if '자)' in s2: a=[x for x in a if x not in (8,10,12,14,16,18,20)] if len(a)>3 else a
    if '개)' in s2: a=a[:3]
    return a
def close(a,b):
    if a<20: return abs(a-b)<=0.6
    if a<=40: return abs(a-b)<=1.5
    if a<=300: return abs(a-b)<=4
    return abs(a-b)<=70
def dims_ok(pd,cd):
    if len(cd)<len(pd): return False
    return all(close(x,y) for x,y in zip(pd,cd))
R=[ # pid-prefix-by-name rules: (name regex on product name, include regex on catalog name, exclude regex)
(r'^구조목 2x',r'구조|2&BTR',r'방부|마감|스프러스 판재|비규격|간주|하부'),
(r'^마감재 스프러스',r'마감용|스프러스 판재',r'2x'),
(r'^다루끼',r'다루끼|한치각',r'LVL|반다루끼|폼|투바이|나왕|라왕'),
(r'^반다루끼',r'반다루끼',r'^$'),
(r'^각재',r'투바이',r'LVL|폼|다루끼 하부'),
(r'^내수합판',r'내수|방수 합판|CP합판',r'석고|준내수'),
(r'^일반합판\(수입\)',r'일반합판|일반 합판|MLH|E1등급',r'국산|라왕|최상급'),
(r'^일반합판\(국산\)',r'일반합판 국산',r'^$'),
(r'^미송',r'미송',r'^$'),(r'^낙엽송',r'낙엽송',r'^$'),(r'^오쿠메',r'오쿠메',r'^$'),(r'^코아',r'코아',r'^$'),(r'^태고',r'태고',r'^$'),
(r'^OSB',r'OSB',r'웨더로직|테크쉴드'),
(r'^MDF',r'MDF',r'고밀도|고비중|타공|방염|10자|9자|템바|UV|uv|컬러|랩핑|오버레이'),
(r'^일반석고',r'일반석고|일반 석고|석고보드 USG',r'방수|방화|차음|평보드|테파드|우드32'),
(r'^방수석고',r'방수\s?석고',r'덴스|방화'),(r'^방화석고',r'방화\s?석고',r'방수'),(r'^차음',r'차음\s?석고',r'^$'),
(r'^방부목 데크',r'데크',r'합성|WPC|라취|방킬라이|적삼'),
(r'^방부각재 2x',r'방부목',r'데크|기둥|크로바|레인|찬넬|규격선택'),
(r'^방부각재$',r'방부',r'데크|크로바홈|크로바 마감|찬넬|레인'),
(r'^방부기둥재',r'크로바',r'마감재'),
(r'^자작합판',r'자작',r'집성'),
]
maxt=max(x['t'] for x in D['prices'])
added=[];matched_cat=set()
for p in D['products']:
    rule=next((r for r in R if re.search(r[0],p['name'])),None)
    if not rule: continue
    pd=pdims(p)
    best={}
    for i,c in enumerate(cat):
        if not re.search(rule[1],c['n']) or re.search(rule[2],c['n']): continue
        bundle=bool(re.search(r'단/|/단|한단|1단|묶음|EA|매/단|入|\d+개',c['n']))
        if bundle!=(p['unit']=='단'): continue
        cd=nums(c['sp'])
        if p['cat']=='자작합판':
            cd=cd[:1]
            if not cd or abs(cd[0]-pd[0])>0.6: continue
        elif not dims_ok(pd,cd): continue
        if p['cat'] in('합판','OSB','MDF') and len(pd)>=3 and len(cd)<3: continue
        if c['s'] not in best or c['v']<best[c['s']][1]['v']: best[c['s']]=(i,c)
    for sid,(i,c) in best.items():
        maxt+=1; matched_cat.add(i)
        added.append(dict(s=sid,p=p['id'],v=c['v'],d='2026-11-05',m=(c['pre']+c['n']).strip(' ·'),t=maxt))
D['prices']+=added
D['catalog']=[dict(s=c['s'],n=c['n'],sp=c['sp'],v=c['v'],vat=bool(c['pre'])) for c in cat]
json.dump(D,open('/home/claude/price-tracker/data.json','w'),ensure_ascii=False,separators=(',',':'))
from collections import Counter
print('catalog',len(cat),'added prices',len(added),'by shop',Counter(a['s'] for a in added))
pn={p['id']:p for p in D['products']}
for a in added[:400]:
    pass
# show mapping sample for sanity
for a in added:
    p=pn[a['p']]; print(p['name'],p['spec'],'<=',a['s'],a['m'],a['v'])

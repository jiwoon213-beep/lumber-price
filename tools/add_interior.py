import json,re
PATH='/home/claude/price-tracker/data.json'
D=json.load(open(PATH))
FILES={'int/daelim_siding.txt':('o01',False),'int/ssakda.txt':('o07',False),'int/kcc.txt':('o12',False),'int/ace_all.txt':('o02',True),
       'int/bds_all.txt':('o16',False),'int/buildhousing_all.txt':('o10',False),'int/daelim_all.txt':('o01',False),'int/diwood_all.txt':('o15',False),'int/hswooda_all.txt':('o08',False),'int/limwood_all.txt':('o09',True),'int/woodnhome_all.txt':('o03',True),'int/baro09_all.txt':('o11',True),'int/hanaro_all.txt':('o21',False),'int/namumok_all.txt':('o18',True)}
have={(c['s'],c['n'],c['v']) for c in D['catalog']}
added=0
for f,(sid,vat) in FILES.items():
    for line in open(f,encoding='utf-8'):
        p=line.rstrip('\n').split('|')
        if len(p)<2 or not p[-1].isdigit(): continue
        n,v=p[0],int(p[-1]); sp=p[1] if len(p)==3 else ''
        m=re.search(r'\s*제조사\s*:\s*(.*?)(?:\s*규격\s*:\s*(.*))?$',n)
        if m:
            n=n[:m.start()].strip(); mk=m.group(1).strip()
            if mk and mk!='-' and mk not in n: n=f'[{mk}] '+n
            if m.group(2) and not sp: sp=m.group(2).strip()
        n=re.sub(r'\s+',' ',n).strip()
        if not n or v<100: continue
        if (sid,n,v) in have: continue
        have.add((sid,n,v)); added+=1
        D['catalog'].append(dict(s=sid,n=n,sp=sp,v=v,vat=vat))
# explicit interior comparison products
F=[
('석고텍스','내장재','박스','9.5T 300x600',r'석고텍스|집텍스',r'(9\.5)',r'MT|마이'),
('마이톤 M바 (MT440)','내장재','박스','12T 300x600',r'마이톤.*(MT440|M바)',r'12T',r'600X600|600x600|이마트|MT441'),
('마이톤 M바 (MT440)','내장재','박스','9T 300x600',r'마이톤.*(MT440|M바)',r'(^|\D)9T',r'600X600|이마트'),
('아이소핑크','단열재','장','30T 900x1800',r'아이소핑크',r'(^|\D)30T',r'^$'),
('아이소핑크','단열재','장','50T 900x1800',r'아이소핑크',r'(^|\D)50T',r'^$'),
('글라스울 24K 50T','단열재','포장','450x1000',r'글라스울|그라스울',r'24K',r'48K|에코배트'),
('석고본드','내장재','포대','25kg',r'석고본드',r'25\s*(kg|KG)',r'^$'),
('아이소핑크','단열재','장','100T 900x1800',r'아이소핑크',r'(^|\D)100T',r'^$'),
('C-스터드 65형','경량철골','M','',r'스터드',r'65형',r'CH|BS|J-|센서|런너'),
('C-스터드 75형','경량철골','M','',r'스터드',r'75형',r'CH|BS|J-|센서|런너'),
('C-런너 65형','경량철골','M','',r'런너',r'65형',r'CH|BS|J-|스터드'),
('타카핀 F30','부자재','통','',r'타카',r'F30',r'스텐|SUS|스테인'),
('타카핀 422J','부자재','통','',r'타카',r'422',r'스텐|SUS'),
]
nid=max(int(p['id'][1:]) for p in D['products']); maxt=max(x['t'] for x in D['prices'])
for name,cat,unit,spec,inc,key,exc in F:
    best={}
    for c in D['catalog']:
        t=c['n']+' '+(c['sp'] or '')
        if re.search(inc,t) and re.search(key,t) and not re.search(exc,t):
            if c['s'] not in best or c['v']<best[c['s']]['v']: best[c['s']]=c
    vs=sorted(c['v'] for c in best.values()); med=vs[len(vs)//2]
    best={k:c for k,c in best.items() if med/2.2<=c['v']<=med*2.2}
    if len(best)<2: print('skip',name,spec,len(best)); continue
    nid+=1; pid='p%02d'%nid
    D['products'].append(dict(id=pid,name=name,spec=spec,unit=unit,cat=cat,key=False))
    for s,c in best.items():
        maxt+=1; D['prices'].append(dict(s=s,p=pid,v=c['v'],d=D['updated'],m=(('VAT별도 · ' if c['vat'] else '')+c['n']).strip(),t=maxt))
    print(pid,name,spec,{s:c['v'] for s,c in best.items()})
json.dump(D,open(PATH,'w'),ensure_ascii=False,separators=(',',':'))
print('catalog +',added,'total',len(D['catalog']),'products',len(D['products']),'prices',len(D['prices']))

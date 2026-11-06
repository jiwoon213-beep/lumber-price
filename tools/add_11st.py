import json
PATH='/home/claude/price-tracker/data.json'
D=json.load(open(PATH))
if not any(s['id']=='o23' for s in D['shops']):
    D['shops'].append(dict(id='o23',name='11번가',url='https://www.11st.co.kr',memo='오픈마켓 최저가 판매자 (배송비 별도인 경우 많음)'))
maxt=max(x['t'] for x in D['prices'])
from statistics import median
add=0
for l in open('int/11st.txt',encoding='utf-8'):
    pid,v,n=l.rstrip('\n').split('|',2); v=int(v)
    ex=[x['v'] for x in D['prices'] if x['p']==pid]
    if ex and not (median(ex)/2.5<=v<=median(ex)*2.5): print('skip',pid,v,median(ex)); continue
    maxt+=1; add+=1; D['prices'].append(dict(s='o23',p=pid,v=v,d=D['updated'],m='11번가 · '+n,t=maxt))
json.dump(D,open(PATH,'w'),ensure_ascii=False,separators=(',',':'))
print('added',add)

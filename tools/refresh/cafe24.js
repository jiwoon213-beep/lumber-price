// Cafe24 쇼핑몰 전체 상품 수집. 쇼핑몰 첫 화면에서 실행 → window.__R.stage==='done' 될 때까지 기다린 뒤
// window.__R.n(줄 수), window.__R.chunks(청크 수) 확인, chunk(i)로 base64(deflate-raw) 조각을 하나씩 받는다.
window.__R={stage:'run',done:0,items:0};
window.chunk=i=>window.__R.z.slice(i*15000,(i+1)*15000);
(async()=>{const R=window.__R;const cats=[...new Set([...document.querySelectorAll('a[href]')].map(a=>{let h;try{h=decodeURI(a.href)}catch(e){h=a.href}const m=h.match(/cate_no=(\d+)|\/category\/[^/]+\/(\d+)\//);return m?(m[1]||m[2]):null}).filter(Boolean))];R.cats=cats.length;const P=new DOMParser();const seen={},all=[];
const go=async no=>{let pf=null;for(let p=1;p<=60;p++){let h;try{h=await(await fetch('/product/list.html?cate_no='+no+'&page='+p)).text()}catch(e){break}const d=P.parseFromString(h,'text/html');const lis=[...d.querySelectorAll('[id^="anchorBoxId_"]')];if(!lis.length||lis[0].id===pf)break;pf=lis[0].id;let nw=0;
for(const li of lis){const id=li.id.slice(12);if(seen[id])continue;seen[id]=1;nw++;const t=li.textContent.replace(/\s+/g,' ').trim();let n=(t.match(/상품명\s*:\s*(.+?)(?=\s*(상품 ?간략설명|상품요약정보|판매가|소비자가|할인판매가|상품가|$))/)||[])[1];if(!n){const e=li.querySelector('.name a,.name,.prdName');n=e?e.textContent.replace(/상품명\s*:/,'').trim():''}if(!n){const im=li.querySelector('img[alt]');n=im?im.alt:''}const m=t.match(/판매가\s*:?\s*([\d,]+)\s*원/);all.push({id,n:n.trim(),v:m?+m[1].replace(/,/g,''):0,so:/품절|SOLD ?OUT/i.test(t)})}R.items=all.length;if(!nw)break;}R.done++;};
for(let i=0;i<cats.length;i+=4)await Promise.all(cats.slice(i,i+4).map(go));
R.stage='det';const need=all.filter(x=>!x.so&&x.n&&!x.v).slice(0,400);
for(let i=0;i<need.length;i+=6){await Promise.all(need.slice(i,i+6).map(async x=>{try{const h=await(await fetch('/product/detail.html?product_no='+x.id)).text();const m=h.match(/product:price:amount"\s*content="([\d.]+)"/);if(m)x.v=Math.round(+m[1])}catch(e){}}))}
const bad=/결제|배송비|운임|샘플|\d{3}-\d{3,4}-\d{2}|현장\)|고객|님 |개인|주문제작|견적/;
const s=new Set(),o=[];for(const x of all){if(x.so||!x.n||x.v<100||bad.test(x.n))continue;const l=x.n.replace(/\|/g,'/').replace(/\s+/g,' ')+'|'+x.v;if(!s.has(l)){s.add(l);o.push(l)}}
const cs=new Blob([o.join('\n')]).stream().pipeThrough(new CompressionStream('deflate-raw'));const buf=new Uint8Array(await new Response(cs).arrayBuffer());let z='';for(const b of buf)z+=String.fromCharCode(b);
R.z=btoa(z);R.n=o.length;R.chunks=Math.ceil(R.z.length/15000);R.stage='done'})().catch(e=>{window.__R.stage='error:'+e});'started'

# 밤 전체 갱신 (쇼핑몰 전체 상품 → 비교 품목 가격)

1. `rotation.json`에서 오늘 요일(월=0)의 쇼핑몰 목록을 고른다.
2. 쇼핑몰마다: 사용자 PC 내장 브라우저로 쇼핑몰 첫 화면을 열고 `cafe24.js` 내용을 그대로 실행 → 30~40초 간격으로
   `({stage:__R.stage,items:__R.items,n:__R.n,chunks:__R.chunks})` 확인. `done`이 되면 `chunk(0)`, `chunk(1)`…을 하나씩 받아
   작업공간 파일(예: /tmp/o08.b64)에 그대로 이어 붙인다. **조각 내용을 절대 지어내지 말 것.**
3. `python3 -c "import base64,zlib;open('/tmp/o08.txt','w').write(zlib.decompress(base64.b64decode(open('/tmp/o08.b64').read().strip()),-15).decode())"`
   줄 수가 `__R.n`과 같은지 확인.
4. `git pull --rebase` 후 `python3 tools/refresh/refresh.py o08 /tmp/o08.txt <오늘 날짜>`.
5. 모든 쇼핑몰 끝나면 `python3 build_sise.py` → data.json·sise.html 커밋·푸시(푸시 거절되면 pull --rebase 후 다시).

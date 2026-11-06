# lumber-price 저장소 규칙 (여러 Claude 세션이 같이 씀)

- 매일 아침 6:37 예약 작업이 data.json에 **오늘 날짜(d)로 새 가격을 추가**하고 `updated`를 오늘로 바꾼 뒤 `python3 build_sise.py`를 실행합니다. 이 기록이 sise.html의 날짜·▲▼ 변동 표시에 쓰입니다.
- data.json을 고칠 때는 **반드시 먼저 `git pull --rebase`** 하고, 최신 파일을 읽어서 그 위에 덧붙이세요. 예전 로컬 사본으로 data.json을 통째로 덮어쓰지 마세요(2026-11-06에 이렇게 해서 그날 가격 61건과 날짜가 사라진 적 있음).
- `updated` 값을 과거 날짜로 되돌리지 마세요. 새 가격을 추가할 때 d에는 **실제 수집한 날짜**를 넣으세요(하드코딩된 '2026-11-05' 금지).
- 다른 날짜의 prices 기록은 지우지 마세요.
- data.json을 바꾼 뒤에는 `python3 build_sise.py` 를 실행해서 sise.html도 같이 커밋하세요.

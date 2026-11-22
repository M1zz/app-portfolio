# 블랙프라이데이 2026 (11/27 ~ 12/3)

| 파일 | 하는 일 |
|---|---|
| apply.py · targets.json | 구독 88개에 신규 첫 기간 80% 할인(11/27~12/4) |
| restore.py · restore.json | 원래 첫 해 할인 12개를 12/4 부터 다시 (11/28 10:00 예약) |
| promo.py · sale-text.json | 프로모션 텍스트를 세일 문구로(11/27 17:05) · 원래대로(12/4 17:05) |
| events.py · event-text.json · make_media.py | App Store 앱 내 이벤트 22개(무지개 공방 제외) |
| link-versions.json | 앱에 요금제 링크(`<번들 ID 소문자>://paywall`)가 처음 들어간 버전 — 이 버전이 나간 뒤에만 이벤트를 낸다 (30분마다 예약) |
| paywall-link.py · release-line.json | 앱 레포에 요금제 링크를 넣는 기계적인 부분(LeeoKit · URL 스킴 · 릴리즈노트) |
| deploy-next.sh | 링크 넣은 앱을 15분마다 하나씩 DeployBar 로 배포 (예약) |

**예약 작업은 `~/.leeo-blackfriday` 사본에서 돈다.** launchd 로 도는 일은 macOS 개인정보 보호 때문에 문서 폴더를 못 읽는다.
그래서 스크립트 · ASC 설정 · 키를 그 폴더에 복사해 두고 `ASC_SHARED` 로 가리킨다. 여기 스크립트를 고치면 그 사본도 같이 고친다.
예약: `~/Library/LaunchAgents/com.leeo.blackfriday-*.plist` (일이 끝나면 각자 지운다).

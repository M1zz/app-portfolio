# purchase-notify

결제가 일어나면 아이폰 · 맥에 바로 알림이 오게 하는 작은 서버.

```
Apple (App Store Server Notifications V2)
  → POST /api/notify       서명을 Apple 루트 인증서까지 확인
  → CloudKit Purchase      iCloud.com.Ysoup.HubPurchases 공개 DB (서버 키, 허브만 쓰는 컨테이너)
  → 허브 앱의 구독          아이폰 · 맥 푸시
```

알리는 것: 새 구독 · 다시 구독 · 갱신 · 일회성 구매 · 할인 코드 구독 · 환불. 나머지 소식은 받기만 하고 버린다.
유료 앱 자체 구매는 Apple 이 하나씩 알려 주지 않는다(판매 보고서로만 안다).

## 환경 변수 (Vercel)

| 이름 | 값 |
|---|---|
| `CK_KEY_ID` | CloudKit Console ▸ Tokens & Keys ▸ Server-to-Server Keys 의 Key ID (Production) |
| `CK_PRIVATE_KEY` | `~/.config/feedbackhub/ck-server-key.pem` 내용 |
| `CK_ENVIRONMENT` | `production` (기본) |

## 앱 목록

`lib/apps.json` — 번들 ID → App Store 앱 ID · 이름. 서명 확인에 앱 ID 가 필요하고, 목록에 없는 앱은 거절한다.
새 앱을 내면 다시 만든다(`scripts/asc-products.py` 의 `ASC` 로 `/v1/apps`).

## App Store Connect

앱마다 ▸ 앱 정보 ▸ App Store 서버 알림: 운영 · 샌드박스 URL 둘 다 `https://<배포 주소>/api/notify`, 버전 2.

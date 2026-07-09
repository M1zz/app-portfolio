# TODO — 앱 마케팅 활동 (2026-07-07)

## 목표
출시 앱 31종 각각을 소개하는 마케팅 콘텐츠 제작 및 발행

## 작업
- [x] 출시 앱 31종 데이터 취합 (앱스토어 캐시 + vision)
- [x] 앱별 마케팅 킷 31종 제작 (`marketing/apps/*.md`)
- [x] 마케팅 인덱스 + 6주 발행 캘린더 (`marketing/README.md`)
- [ ] **사용자 작업**: 킷 검토 후 발행 채널 결정 (X/Threads, 인스타, 디스콰이엇 등)
- [ ] 실제 게시 (사용자 확인 후)

---

# TODO — 포트폴리오 GitHub Pages 배포

## 목표
앱 포트폴리오를 공개 쇼케이스로 정리해 GitHub Pages에 자동 배포

## 작업
- [x] 데이터 구조 / 기존 워크플로우 파악
- [x] 앱스토어(iTunes Lookup) API 검증
- [x] 사이트 빌드 스크립트 작성 (`scripts/build-portfolio-site.py`)
  - [x] 앱 JSON 로드 + appStoreId 추출
  - [x] 앱스토어에서 아이콘/평점/장르/가격/설명 자동 수집 + 캐시 (KR→US→JP 폴백)
  - [x] 반응형 쇼케이스 `docs/index.html` 생성
- [x] GitHub Actions 워크플로우 작성 (`deploy-pages.yml`, 자동 빌드 & 배포)
- [x] 로컬 빌드 테스트 (출시 16 / 전체 19, 스크린샷 확인)
- [x] README / setup 문서 링크 갱신
- [x] README에 앱 목록 표 자동 생성 (APPS:START/END 마커, 빌드 시 갱신)
- [ ] **사용자 작업**: GitHub Settings → Pages → Source = "GitHub Actions" (최초 1회)
- [ ] 커밋 & push (사용자 요청 시)

## 결정 사항
- 목적: 공개 앱 쇼케이스
- 이미지: 앱스토어에서 자동 수집
- 배포: GitHub Actions 자동 빌드

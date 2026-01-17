# 🌐 GitHub Pages 대시보드 설정 가이드

Git repo를 활용해서 어디서든 대시보드를 볼 수 있도록 설정하는 방법입니다.

## 🚀 설정 방법 (5분)

### 1단계: GitHub에 Push
```bash
git add .
git commit -m "🎉 Add GitHub Pages dashboard"
git push origin main
```

### 2단계: GitHub Pages 활성화

1. GitHub 저장소로 이동
2. **Settings** 클릭
3. 왼쪽 메뉴에서 **Pages** 클릭
4. **Source**를 `Deploy from a branch`로 설정
5. **Branch**를 `main` 선택, 폴더를 `/docs` 선택
6. **Save** 클릭

![GitHub Pages 설정](https://docs.github.com/assets/cb-47267/images/help/pages/publishing-source-drop-down.png)

### 3단계: URL 확인

약 1-2분 후 다음 URL에서 대시보드를 볼 수 있습니다:

```
https://[YOUR-USERNAME].github.io/app-portfolio/
```

예시:
- https://leeo.github.io/app-portfolio/
- https://hyunholee.github.io/app-portfolio/

---

## ✨ 자동 업데이트 설정

### GitHub Actions 활성화

이미 `.github/workflows/update-dashboard.yml`이 설정되어 있습니다.

**작동 방식:**
1. `apps/*.json` 파일을 수정하고 push
2. GitHub Actions가 자동으로 실행
3. 대시보드 자동 재생성 및 배포
4. 1-2분 후 웹에서 자동 업데이트 확인

**수동 실행:**
1. GitHub 저장소 → **Actions** 탭
2. **Update Portfolio Dashboard** 선택
3. **Run workflow** 클릭

---

## 📊 README에 대시보드 링크 추가

### README.md 상단에 추가하세요:

```markdown
# 🍎 Leeo's App Portfolio

[![Dashboard](https://img.shields.io/badge/📊_Live_Dashboard-보기-blue?style=for-the-badge)](https://[YOUR-USERNAME].github.io/app-portfolio/)
[![Stats](https://img.shields.io/badge/📈_Statistics-보기-green?style=for-the-badge)](./STATS.md)

> 🌐 **실시간 대시보드**: 어디서든 브라우저로 포트폴리오 현황 확인

자세한 통계는 [STATS.md](STATS.md)를 확인하세요.
```

`[YOUR-USERNAME]`을 본인의 GitHub 유저네임으로 변경하세요.

---

## 🎯 활용 방법

### 1. 모바일에서 확인
스마트폰 브라우저에서 GitHub Pages URL을 열어 언제 어디서든 확인

### 2. 북마크 등록
자주 보는 URL을 북마크에 등록

### 3. 팀원과 공유
URL을 공유하면 누구나 현황 확인 가능

### 4. 포트폴리오 제출
취업/프리랜서 제안 시 URL 첨부

---

## 🔄 대시보드 업데이트 워크플로우

### 로컬에서 작업 후:
```bash
# 1. 태스크 업데이트
./scripts/claude-update-task.sh "앱이름" "태스크" "done"

# 2. Git에 커밋
git add .
git commit -m "Update: 앱이름 - 태스크 완료"
git push

# 3. 1-2분 후 웹 대시보드 자동 업데이트 ✨
```

### GitHub에서 직접 수정:
1. GitHub 웹에서 `apps/*.json` 파일 수정
2. Commit changes
3. 자동으로 대시보드 업데이트

---

## 📱 추가 기능

### 1. STATS.md 페이지
GitHub에서 바로 볼 수 있는 통계 페이지가 자동 생성됩니다:
- 실시간 통계 뱃지
- 상세 현황 테이블
- 우선순위 높은 앱 목록

링크: `https://github.com/[YOUR-USERNAME]/app-portfolio/blob/main/STATS.md`

### 2. 모바일 최적화
대시보드는 반응형으로 제작되어 모바일에서도 깔끔하게 보입니다.

### 3. 오프라인 접근
`dashboard/index.html`을 로컬에서도 언제든지 열 수 있습니다:
```bash
./scripts/open-dashboard.sh
```

---

## 🐛 문제 해결

### GitHub Pages가 활성화되지 않는 경우
- 저장소가 Public인지 확인 (Private은 Pro 계정 필요)
- Settings → Pages에서 올바르게 설정되었는지 확인
- `docs/index.html` 파일이 존재하는지 확인

### 대시보드가 업데이트되지 않는 경우
1. GitHub Actions가 실행되었는지 확인 (Actions 탭)
2. 에러가 있는지 로그 확인
3. 브라우저 캐시 삭제 (Cmd+Shift+R 또는 Ctrl+Shift+R)

### Actions 실행 권한 오류
1. Settings → Actions → General
2. **Workflow permissions**를 "Read and write permissions"로 변경
3. **Save** 클릭

---

## 🎨 대시보드 커스터마이징

대시보드 디자인을 수정하려면:

1. `scripts/generate-dashboard.py` 파일 수정
2. 로컬에서 테스트:
   ```bash
   python3 scripts/generate-dashboard.py
   open dashboard/index.html
   ```
3. 만족하면 커밋 & 푸시

---

## 📚 참고 문서

- [GitHub Pages 공식 문서](https://docs.github.com/en/pages)
- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
- [본 프로젝트 자동화 가이드](AUTOMATION-GUIDE.md)

---

## 💡 고급 활용

### Custom Domain 설정
본인의 도메인을 연결하려면:
1. DNS 설정에서 CNAME 레코드 추가
2. GitHub Pages 설정에서 Custom domain 입력
3. 예시: `portfolio.leeo.dev`

### PWA로 변환
대시보드를 앱처럼 설치 가능하게 만들려면 `manifest.json` 추가

### 실시간 업데이트
WebSocket이나 Server-Sent Events로 자동 새로고침 구현 가능

---

이제 어디서든 브라우저만 있으면 포트폴리오를 확인할 수 있습니다! 🎉

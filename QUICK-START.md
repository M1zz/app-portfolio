# ⚡ 빠른 시작 가이드

포트폴리오 자동화 시스템을 5분 안에 시작하는 방법입니다.

## 🎯 목표

- ✅ 로컬 대시보드 확인
- ✅ 태스크 업데이트 해보기
- ✅ GitHub Pages로 온라인 배포

---

## 1️⃣ 로컬 대시보드 확인 (30초)

```bash
./scripts/open-dashboard.sh
```

브라우저가 자동으로 열리고 23개 앱의 현황을 시각적으로 확인할 수 있습니다.

---

## 2️⃣ 태스크 업데이트 해보기 (1분)

```bash
# 예시: 리바운드 저널의 "머지 컨플릭트 PR" 완료 처리
./scripts/claude-update-task.sh "리바운드 저널" "머지 컨플릭트 PR" "done"

# 대시보드 새로고침
./scripts/open-dashboard.sh
```

**상태 옵션:**
- `done` - 완료
- `in-progress` - 진행 중
- `not-started` - 미시작

---

## 3️⃣ 우선순위 분석 (30초)

```bash
./scripts/claude-priority-analysis.sh
```

AI가 다음 주 작업 우선순위를 분석해서 제안합니다.

---

## 4️⃣ GitHub Pages 배포 (3분)

### 4-1. 저장소 Push
```bash
git add .
git commit -m "🎉 Setup portfolio automation"
git push origin main
```

### 4-2. GitHub Pages 활성화

1. GitHub 저장소 → **Settings** 클릭
2. 왼쪽 메뉴 → **Pages** 클릭
3. **Source**: `Deploy from a branch`
4. **Branch**: `main` / **Folder**: `/docs`
5. **Save** 클릭

### 4-3. URL 확인 (1-2분 대기)

```
https://hyunholee.github.io/app-portfolio/
```

본인의 GitHub 유저네임으로 URL을 변경하세요.

---

## 🎨 자주 사용하는 명령어

### 앱 상태 조회
```bash
./scripts/claude-app-status.sh "라포 맵"
```

### 주간 리포트 생성
```bash
./scripts/claude-weekly-report.sh
```

### 릴리스 노트 생성
```bash
./scripts/claude-release.sh "두 번 알림" "1.0.6"
```

### 데이터 검증
```bash
python3 scripts/validate-portfolio.py
```

---

## 🔄 일상적인 워크플로우

### 아침 루틴
```bash
# 대시보드 확인
./scripts/open-dashboard.sh

# 우선순위 분석
./scripts/claude-priority-analysis.sh
```

### 개발 중
```bash
# 태스크 진행 시작
./scripts/claude-update-task.sh "세끼" "식단 피드백 기능" "in-progress"

# ... 개발 ...

# 태스크 완료
./scripts/claude-update-task.sh "세끼" "식단 피드백 기능" "done"
```

### 배포 준비
```bash
# 릴리스 노트 생성
./scripts/claude-release.sh "세끼" "1.0.4"

# GitHub Pages 배포
./scripts/deploy-github-pages.sh
```

---

## 📱 어디서든 확인하기

### GitHub 웹에서
- **실시간 통계**: [STATS.md](https://github.com/hyunholee/app-portfolio/blob/main/STATS.md)
- **대시보드**: https://hyunholee.github.io/app-portfolio/

### 모바일에서
- 스마트폰 브라우저에서 GitHub Pages URL 열기
- 북마크에 저장하면 앱처럼 빠르게 접근

---

## 🆘 도움말

### 전체 가이드
- [AUTOMATION-GUIDE.md](AUTOMATION-GUIDE.md) - 자동화 시스템 상세 가이드
- [GITHUB-PAGES-SETUP.md](GITHUB-PAGES-SETUP.md) - GitHub Pages 설정 가이드
- [CLAUDE-GUIDE.md](CLAUDE-GUIDE.md) - Claude 데이터 관리 가이드

### 스크립트 실행 권한 오류 시
```bash
chmod +x scripts/*.sh scripts/*.py
```

### Python 버전 확인
```bash
python3 --version  # 3.7 이상 필요
```

---

## 💡 다음 단계

익숙해지면 다음 기능들을 활용해보세요:

1. **GitHub Actions 자동화**
   - 파일 수정하면 자동으로 대시보드 업데이트
   - 이미 설정되어 있습니다!

2. **프롬프트 템플릿 활용**
   - `prompts/` 폴더의 템플릿으로 반복 작업 자동화

3. **Git Hook 활용**
   - 커밋 전 자동 검증으로 데이터 무결성 보장

4. **alias 설정**
   ```bash
   # ~/.zshrc 또는 ~/.bashrc에 추가
   alias pd='cd ~/path/to/app-portfolio && ./scripts/open-dashboard.sh'
   alias pp='cd ~/path/to/app-portfolio && ./scripts/claude-priority-analysis.sh'
   ```

---

## ✨ 팁

1. **매일 아침** 대시보드로 하루 시작
2. **태스크 완료 즉시** 스크립트로 업데이트
3. **주말마다** 주간 리포트 생성
4. **배포 전** 릴리스 노트 자동 생성

---

이제 시작할 준비가 되었습니다! 🚀

첫 명령어: `./scripts/open-dashboard.sh`

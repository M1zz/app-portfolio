# 🤖 자동화 시스템 사용 가이드

Leeo의 20개 앱 포트폴리오를 효율적으로 관리하기 위한 자동화 도구 모음입니다.

## 📁 구조

```
app-portfolio/
├── scripts/                      # 자동화 스크립트
│   ├── claude-update-task.sh     # 태스크 업데이트
│   ├── claude-weekly-report.sh   # 주간 리포트 생성
│   ├── claude-release.sh         # 릴리스 노트 생성
│   ├── claude-priority-analysis.sh # 우선순위 분석
│   ├── claude-app-status.sh      # 앱 상태 조회
│   ├── validate-portfolio.py     # 데이터 검증
│   ├── generate-dashboard.py     # 대시보드 생성
│   └── open-dashboard.sh         # 대시보드 열기
├── prompts/                      # Claude 프롬프트 템플릿
│   ├── deploy-checklist.txt      # 배포 체크리스트
│   ├── bug-investigation.txt     # 버그 조사
│   ├── feature-planning.txt      # 기능 기획
│   └── code-review.txt           # 코드 리뷰
├── dashboard/                    # 시각적 대시보드
│   └── index.html
└── .git/hooks/                   # Git 자동화
    └── pre-commit                # 커밋 전 검증
```

---

## 🚀 빠른 시작

### 1. 대시보드 보기
```bash
./scripts/open-dashboard.sh
```
브라우저에서 모든 앱의 현황을 한눈에 확인할 수 있습니다.

### 2. 태스크 업데이트
```bash
./scripts/claude-update-task.sh "라포 맵" "클라우드 백업기능" "done"
```

### 3. 주간 리포트 생성
```bash
./scripts/claude-weekly-report.sh
```

### 4. 우선순위 분석
```bash
./scripts/claude-priority-analysis.sh
```

---

## 📋 스크립트 상세 설명

### 1. claude-update-task.sh
**기능**: 특정 앱의 태스크 상태를 자동으로 업데이트

**사용법**:
```bash
./scripts/claude-update-task.sh "앱이름" "태스크명" "상태"
```

**예시**:
```bash
# 태스크 완료 처리
./scripts/claude-update-task.sh "두 번 알림" "아이클라우드 동기화" "done"

# 태스크 진행 중으로 변경
./scripts/claude-update-task.sh "세끼" "식단 피드백 기능" "in-progress"

# 태스크 대기로 변경
./scripts/claude-update-task.sh "나만의 버킷" "이미지 올리기" "not-started"
```

**자동 처리**:
- ✅ stats 재계산 (totalTasks, done, inProgress, notStarted)
- ✅ nextTasks 배열 업데이트
- ✅ recentlyCompleted 배열 업데이트
- ✅ portfolio-summary.json 재생성

---

### 2. claude-weekly-report.sh
**기능**: 이번 주 진행 상황을 자동으로 정리한 리포트 생성

**사용법**:
```bash
./scripts/claude-weekly-report.sh
```

**생성 내용**:
- 이번 주 완료된 태스크 목록
- 현재 진행 중인 태스크
- 다음 주 계획
- 주요 지표 변화
- 배포 예정 앱

**출력**: `reports/weekly-YYYY-MM-DD.md`

---

### 3. claude-release.sh
**기능**: 앱 배포용 릴리스 노트 자동 생성

**사용법**:
```bash
./scripts/claude-release.sh "앱이름" "버전"
```

**예시**:
```bash
./scripts/claude-release.sh "두 번 알림" "1.0.6"
```

**생성 내용**:
- 🎉 새로운 기능
- 🔧 개선사항
- 🐛 버그 수정
- 📝 기타 변경사항
- 앱스토어용 간략 버전 (500자)

**자동 처리**:
- ✅ 앱의 currentVersion 업데이트

---

### 4. claude-priority-analysis.sh
**기능**: AI 기반 우선순위 분석 및 다음 주 작업 제안

**사용법**:
```bash
./scripts/claude-priority-analysis.sh
```

**분석 내용**:
- 🔥 긴급 태스크 (이번 주 필수)
- ⭐ 중요 태스크 (이번 주 권장)
- 💡 제안 태스크 (여유 있으면)
- 📊 현황 요약

**평가 기준**:
- 우선순위 높은 앱의 진행 중 태스크
- 배포 임박한 앱 (완료율 80% 이상)
- 오래 방치된 태스크
- Quick wins (빠르게 완료 가능한 것)

---

### 5. claude-app-status.sh
**기능**: 특정 앱의 상세 상태 조회

**사용법**:
```bash
./scripts/claude-app-status.sh "앱이름"
```

**예시**:
```bash
./scripts/claude-app-status.sh "라포 맵"
```

**조회 내용**:
- 기본 정보 (버전, 상태, 우선순위)
- 진행 현황 (태스크 통계)
- 다음 할 일 목록
- 최근 완료 작업
- 진행 중인 태스크 상세
- 간단한 분석 및 제안

---

### 6. validate-portfolio.py
**기능**: 포트폴리오 데이터 무결성 자동 검증

**사용법**:
```bash
python3 scripts/validate-portfolio.py
```

**검증 항목**:
- ✅ JSON 파일 형식 검증
- ✅ 필수 필드 존재 여부
- ✅ status, priority 값 유효성
- ✅ stats와 allTasks 동기화 확인
- ✅ 버전 형식 확인

**자동 실행**:
- Git 커밋 전 자동 실행 (pre-commit hook)
- 검증 실패 시 커밋 차단

---

### 7. generate-dashboard.py
**기능**: HTML 기반 시각적 대시보드 생성

**사용법**:
```bash
python3 scripts/generate-dashboard.py

# 또는 생성 + 브라우저에서 열기
./scripts/open-dashboard.sh
```

**대시보드 기능**:
- 📊 전체 통계 요약
- 🔥 우선순위 높은 앱 하이라이트
- 📱 전체 활성 앱 목록
- 📈 진행률 시각화
- 📋 다음 할 일 미리보기

**자동 새로고침**:
데이터 변경 후 스크립트 재실행하면 대시보드 자동 업데이트

---

## 📝 프롬프트 템플릿 사용법

### 배포 체크리스트
```bash
# prompts/deploy-checklist.txt 수정 후
cat prompts/deploy-checklist.txt | sed 's/{앱이름}/두 번 알림/g; s/{버전}/1.0.6/g' | claude
```

### 버그 조사
```bash
# prompts/bug-investigation.txt 수정 후
cat prompts/bug-investigation.txt | \
  sed 's/{앱이름}/라포 맵/g; s/{버그 설명}/크래시 발생/g' | \
  claude
```

### 새 기능 기획
```bash
cat prompts/feature-planning.txt | \
  sed 's/{앱이름}/세끼/g; s/{기능 설명}/사진 추가 기능/g' | \
  claude
```

### 코드 리뷰
```bash
cat prompts/code-review.txt | \
  sed 's/{앱이름}/리바운드 저널/g; s/{번호}/42/g' | \
  claude
```

---

## 🔄 일상적인 워크플로우

### 아침 루틴
```bash
# 1. 대시보드 확인
./scripts/open-dashboard.sh

# 2. 우선순위 분석
./scripts/claude-priority-analysis.sh

# 3. 특정 앱 상태 확인
./scripts/claude-app-status.sh "라포 맵"
```

### 개발 중
```bash
# 태스크 진행 중으로 변경
./scripts/claude-update-task.sh "세끼" "식단 피드백 기능" "in-progress"

# ... 개발 ...

# 태스크 완료 처리
./scripts/claude-update-task.sh "세끼" "식단 피드백 기능" "done"

# 대시보드 업데이트
python3 scripts/generate-dashboard.py
```

### 배포 준비
```bash
# 1. 릴리스 노트 생성
./scripts/claude-release.sh "두 번 알림" "1.0.6"

# 2. 데이터 검증
python3 scripts/validate-portfolio.py

# 3. Git 커밋
git add .
git commit -m "Release: 두 번 알림 v1.0.6"
```

### 주말 정리
```bash
# 주간 리포트 생성
./scripts/claude-weekly-report.sh

# 리포트 확인
cat reports/weekly-$(date +%Y-%m-%d).md
```

---

## ⚙️ 고급 활용

### 1. 여러 태스크 일괄 업데이트
```bash
# 스크립트 작성
cat > bulk-update.sh << 'EOF'
#!/bin/bash
./scripts/claude-update-task.sh "라포 맵" "클라우드 백업" "done"
./scripts/claude-update-task.sh "세끼" "간식 감추기" "done"
./scripts/claude-update-task.sh "나만의 버킷" "타임라인 레이아웃" "in-progress"
EOF

chmod +x bulk-update.sh
./bulk-update.sh
```

### 2. 크론잡으로 자동 리포트
```bash
# 매주 금요일 오후 5시에 주간 리포트 생성
crontab -e

# 추가:
0 17 * * 5 cd /path/to/app-portfolio && ./scripts/claude-weekly-report.sh
```

### 3. Claude와 대화형 작업
```bash
# Claude에게 직접 명령
claude "라포 맵의 진행 중인 태스크 중 하나를 완료 처리하고, 우선순위 재분석해줘"

# 또는 프롬프트 파일 사용
claude < prompts/feature-planning.txt
```

### 4. 대시보드 자동 새로고침
```bash
# watch 명령으로 5초마다 대시보드 재생성
watch -n 5 python3 scripts/generate-dashboard.py
```

---

## 🐛 문제 해결

### 스크립트 실행 권한 오류
```bash
# 모든 스크립트에 실행 권한 부여
chmod +x scripts/*.sh scripts/*.py
```

### Python 버전 확인
```bash
python3 --version
# Python 3.7 이상 필요
```

### Git hook이 작동하지 않음
```bash
# hook 실행 권한 확인
chmod +x .git/hooks/pre-commit

# hook 테스트
.git/hooks/pre-commit
```

### Claude 명령어를 찾을 수 없음
```bash
# Claude CLI 설치 확인
which claude

# 또는 전체 경로 사용
/usr/local/bin/claude
```

---

## 📈 다음 단계 (Phase 2)

Phase 1 자동화에 익숙해지면:

1. **GitHub Actions 설정**
   - PR 자동 리뷰
   - 자동 테스트
   - 자동 배포

2. **공유 모듈 추출**
   - 중복 코드 통합
   - SPM 패키지 관리

3. **CI/CD 파이프라인**
   - TestFlight 자동 업로드
   - 앱스토어 자동 제출

4. **모니터링 시스템**
   - 크래시 자동 분석
   - 리뷰 자동 수집
   - 성능 트래킹

---

## 💡 팁

1. **alias 설정**으로 더 빠르게
```bash
# ~/.zshrc 또는 ~/.bashrc에 추가
alias portfolio-dash='cd ~/path/to/app-portfolio && ./scripts/open-dashboard.sh'
alias portfolio-report='cd ~/path/to/app-portfolio && ./scripts/claude-weekly-report.sh'
alias portfolio-priority='cd ~/path/to/app-portfolio && ./scripts/claude-priority-analysis.sh'
```

2. **VS Code 태스크** 설정
```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Open Portfolio Dashboard",
      "type": "shell",
      "command": "./scripts/open-dashboard.sh"
    }
  ]
}
```

3. **정기적인 검증** 습관화
```bash
# 매일 아침 실행
python3 scripts/validate-portfolio.py && ./scripts/open-dashboard.sh
```

---

## 🎯 목표

이 자동화 시스템의 목표:
- ⏱️ **75% 시간 절약** (월 120시간 → 30시간)
- 🎯 **우선순위 명확화** (AI 기반 제안)
- 📊 **실시간 가시성** (대시보드)
- ✅ **데이터 무결성** (자동 검증)
- 🚀 **빠른 배포** (자동화된 워크플로우)

---

*마지막 업데이트: 2026-01-17*

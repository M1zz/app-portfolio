# 🤖 Claude 포트폴리오 관리 가이드

이 가이드는 Claude가 Leeo의 앱 포트폴리오를 효과적으로 관리하기 위한 지침입니다.

## 📋 데이터 구조

### portfolio-summary.json
전체 포트폴리오의 요약 정보. 읽기 전용으로 사용하고, 앱 데이터 변경 시 자동 재생성 필요.

### apps/{app-name}.json
각 앱의 상세 정보와 태스크 목록.

```json
{
  "name": "한글 앱 이름",
  "nameEn": "English Name",
  "bundleId": "com.leeo.appname",
  "currentVersion": "1.0.0",
  "status": "active|planning|maintenance|archived",
  "priority": "high|medium|low",
  "minimumOS": "16.0",
  "sharedModules": ["ModuleName"],
  "appStoreId": "123456789",
  "githubRepo": "leeo/repo-name",
  "stats": {
    "totalTasks": 10,
    "done": 5,
    "inProgress": 2,
    "notStarted": 3
  },
  "nextTasks": ["다음 할 일 1", "다음 할 일 2"],
  "recentlyCompleted": ["완료된 작업 1"],
  "allTasks": [
    {
      "name": "태스크 이름",
      "status": "done|in-progress|not-started",
      "targetDate": "December 1, 2025",
      "targetVersion": "1.0.1"
    }
  ],
  "notes": "메모"
}
```

## 🔧 주요 작업 패턴

### 1. 태스크 상태 변경
```python
# 태스크를 완료로 변경
task['status'] = 'done'

# stats 업데이트
app['stats']['done'] += 1
app['stats']['inProgress'] -= 1

# nextTasks, recentlyCompleted 업데이트
app['recentlyCompleted'].insert(0, task['name'])
app['nextTasks'].remove(task['name'])
```

### 2. 버전 업데이트
```python
app['currentVersion'] = "2.0.0"
# 관련 태스크들의 targetVersion도 확인
```

### 3. 새 태스크 추가
```python
new_task = {
    "name": "새로운 기능",
    "status": "not-started",
    "targetDate": None,
    "targetVersion": "1.1.0"
}
app['allTasks'].append(new_task)
app['stats']['totalTasks'] += 1
app['stats']['notStarted'] += 1
```

### 4. 포트폴리오 요약 재생성
앱 데이터 변경 후 반드시 portfolio-summary.json 재생성 필요.

## 📊 리포트 생성 템플릿

### 주간 리포트 (reports/weekly-YYYY-MM-DD.md)
```markdown
# 주간 리포트: YYYY-MM-DD

## 이번 주 완료
- [앱명] 태스크명

## 진행 중
- [앱명] 태스크명

## 다음 주 계획
- [앱명] 태스크명

## 배포
- 앱명 v버전 배포 완료/예정
```

## ⚠️ 주의사항

1. **stats는 항상 allTasks와 동기화** - 태스크 변경 시 stats도 함께 업데이트
2. **bundleId 형식** - `com.leeo.{앱영문명소문자}`
3. **파일명 형식** - 영문 소문자, 하이픈 구분 (예: `clip-keyboard.json`)
4. **날짜 형식** - "December 1, 2025" (Notion 원본 형식 유지)

## 🔍 자주 쓰는 쿼리

```
# 우선순위 높은 앱
[a for a in apps if a['priority'] == 'high']

# 진행 중인 태스크가 있는 앱
[a for a in apps if a['stats']['inProgress'] > 0]

# 특정 모듈을 사용하는 앱
[a for a in apps if 'ModuleName' in a['sharedModules']]
```

---

이 가이드를 참고하여 데이터를 일관성 있게 관리해주세요.

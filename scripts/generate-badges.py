#!/usr/bin/env python3
"""
README.md용 통계 뱃지 생성
GitHub에서 보기 좋은 통계 마크다운 생성
"""

import json
from pathlib import Path

def generate_badges():
    root_dir = Path(__file__).parent.parent
    summary_file = root_dir / "portfolio-summary.json"

    with open(summary_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    overview = data.get('overview', {})
    total_apps = data.get('totalApps', 0)
    active = overview.get('active', 0)
    total_tasks = overview.get('totalTasks', 0)
    total_done = overview.get('totalDone', 0)
    total_in_progress = overview.get('totalInProgress', 0)
    high_priority = overview.get('highPriority', 0)

    completion_rate = (total_done / total_tasks * 100) if total_tasks > 0 else 0

    # 색상 결정
    if completion_rate >= 70:
        progress_color = 'success'
    elif completion_rate >= 40:
        progress_color = 'yellow'
    else:
        progress_color = 'orange'

    # 뱃지 생성
    badges_md = f"""
## 📊 실시간 통계

![Total Apps](https://img.shields.io/badge/Total_Apps-{total_apps}-blue?style=for-the-badge&logo=apple)
![Active Apps](https://img.shields.io/badge/Active_Apps-{active}-green?style=for-the-badge&logo=checkmark)
![High Priority](https://img.shields.io/badge/High_Priority-{high_priority}-red?style=for-the-badge&logo=alert)
![Progress](https://img.shields.io/badge/Progress-{completion_rate:.1f}%25-{progress_color}?style=for-the-badge)
![Tasks Done](https://img.shields.io/badge/Tasks_Done-{total_done}/{total_tasks}-{progress_color}?style=for-the-badge)
![In Progress](https://img.shields.io/badge/In_Progress-{total_in_progress}-orange?style=for-the-badge)

> 🌐 **[라이브 대시보드 보기 →](https://[YOUR-USERNAME].github.io/app-portfolio/)**

"""

    # 상세 통계 테이블
    stats_table = f"""
## 📈 상세 현황

| 카테고리 | 수치 | 진행률 |
|---------|------|--------|
| 전체 앱 | {total_apps}개 | - |
| 활성 앱 | {active}개 | {active/total_apps*100:.1f}% |
| 우선순위 높음 | {high_priority}개 | {high_priority/total_apps*100:.1f}% |
| 전체 태스크 | {total_tasks}개 | - |
| ✅ 완료 | {total_done}개 | {completion_rate:.1f}% |
| 🔄 진행 중 | {total_in_progress}개 | {total_in_progress/total_tasks*100:.1f}% |
| ⏸️ 대기 | {overview.get('totalNotStarted', 0)}개 | {overview.get('totalNotStarted', 0)/total_tasks*100:.1f}% |

"""

    # 우선순위 높은 앱 목록
    apps = data.get('apps', [])
    high_priority_apps = [app for app in apps if app.get('priority') == 'high']

    priority_list = "\n## 🔥 우선순위 높은 앱\n\n"
    for app in high_priority_apps[:10]:  # 상위 10개
        stats = app.get('stats', {})
        total = stats.get('totalTasks', 0)
        done = stats.get('done', 0)
        progress = (done / total * 100) if total > 0 else 0

        # 진행률 바
        filled = int(progress / 10)
        bar = '█' * filled + '░' * (10 - filled)

        next_task = app.get('nextTasks', ['없음'])[0]

        priority_list += f"- **{app.get('name')}** v{app.get('currentVersion')} "
        priority_list += f"`{bar}` {progress:.0f}% ({done}/{total})\n"
        priority_list += f"  - 다음: {next_task}\n"

    # 파일에 저장
    output_file = root_dir / "STATS.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(badges_md)
        f.write(stats_table)
        f.write(priority_list)
        f.write(f"\n---\n\n*자동 생성: GitHub Actions로 자동 업데이트*\n")

    print(f"✅ 통계 페이지 생성: {output_file}")
    print("\n📋 README.md에 다음을 추가하세요:")
    print("\n```markdown")
    print("[![Dashboard](https://img.shields.io/badge/📊_Dashboard-보기-blue?style=for-the-badge)](https://[YOUR-USERNAME].github.io/app-portfolio/)")
    print("\n자세한 통계는 [STATS.md](STATS.md)를 확인하세요.")
    print("```")

if __name__ == "__main__":
    generate_badges()

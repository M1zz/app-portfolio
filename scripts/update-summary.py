#!/usr/bin/env python3
"""
portfolio-summary.json 자동 생성 스크립트
apps/*.json 파일들을 읽어서 summary 파일 생성
"""

import json
from pathlib import Path
from datetime import datetime

def main():
    root_dir = Path(__file__).parent.parent
    apps_dir = root_dir / "apps"
    summary_file = root_dir / "portfolio-summary.json"

    print("📊 portfolio-summary.json 업데이트 중...\n")

    # 모든 앱 데이터 로드
    apps_data = []
    for json_file in sorted(apps_dir.glob("*.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                app = json.load(f)
                apps_data.append({
                    "name": app.get("name", ""),
                    "nameEn": app.get("nameEn", ""),
                    "file": json_file.name,
                    "currentVersion": app.get("currentVersion", "1.0.0"),
                    "status": app.get("status", "planning"),
                    "priority": app.get("priority", "medium"),
                    "stats": app.get("stats", {
                        "totalTasks": 0,
                        "done": 0,
                        "inProgress": 0,
                        "notStarted": 0
                    }),
                    "nextTasks": app.get("nextTasks", [])[:2]  # 최대 2개
                })
                print(f"  ✅ {json_file.name}")
        except Exception as e:
            print(f"  ❌ {json_file.name}: {e}")

    # 통계 계산
    total_apps = len(apps_data)
    active_count = sum(1 for app in apps_data if app["status"] == "active")
    planning_count = sum(1 for app in apps_data if app["status"] == "planning")
    high_priority_count = sum(1 for app in apps_data if app["priority"] == "high")

    total_tasks = sum(app["stats"].get("totalTasks", 0) for app in apps_data)
    total_done = sum(app["stats"].get("done", 0) for app in apps_data)
    total_in_progress = sum(app["stats"].get("inProgress", 0) for app in apps_data)
    total_not_started = sum(app["stats"].get("notStarted", 0) for app in apps_data)

    # Summary 생성
    summary = {
        "lastUpdated": datetime.now().isoformat(),
        "totalApps": total_apps,
        "overview": {
            "active": active_count,
            "planning": planning_count,
            "highPriority": high_priority_count,
            "totalTasks": total_tasks,
            "totalDone": total_done,
            "totalInProgress": total_in_progress,
            "totalNotStarted": total_not_started
        },
        "apps": apps_data
    }

    # 파일 저장
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n✅ portfolio-summary.json 업데이트 완료!")
    print(f"   - 총 앱: {total_apps}개")
    print(f"   - 활성: {active_count}개, 기획: {planning_count}개")
    print(f"   - 태스크: {total_done}/{total_tasks} 완료")

if __name__ == "__main__":
    main()

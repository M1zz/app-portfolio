#!/usr/bin/env python3
"""
각 앱에서 feature로 분류되지 않은 태스크들을 찾는 스크립트
"""

import json
from pathlib import Path

APPS_DIR = Path("/Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO/Data/apps")


def should_be_feature(task_name):
    """태스크가 feature로 분류될 수 있는지 판단"""
    # 제외할 패턴
    exclude_patterns = [
        "배포", "출시", "릴리즈", "release",
        "버그", "BUG", "[BUG]", "bug fix",
        "앱 구상", "기획",
        "사용성 개선",
        "리팩토링", "refactor",
        "테스트", "test",
        "문서", "documentation"
    ]

    task_lower = task_name.lower()

    for pattern in exclude_patterns:
        if pattern.lower() in task_lower:
            return False

    # 너무 짧거나 모호한 이름
    if len(task_name) < 3:
        return False

    return True


def main():
    """메인 실행"""
    print("=" * 80)
    print("Feature로 분류되지 않은 태스크 찾기")
    print("=" * 80)
    print()

    app_files = sorted(APPS_DIR.glob("*.json"))

    for app_file in app_files:
        with open(app_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        app_name = data.get('name', app_file.stem)
        all_tasks = data.get('allTasks', [])

        # feature가 아닌 태스크 찾기
        non_features = []
        for task in all_tasks:
            # feature 라벨이나 metadata가 없고
            has_feature_label = 'labels' in task and 'feature' in task.get('labels', [])
            has_feature_meta = 'featureMetadata' in task and task['featureMetadata']

            if not has_feature_label and not has_feature_meta:
                # feature가 될 수 있는지 판단
                if should_be_feature(task['name']):
                    non_features.append(task['name'])

        if non_features:
            print(f"\n## {app_name} ({app_file.stem})")
            print(f"   Feature 후보: {len(non_features)}개")
            for task_name in non_features:
                print(f"   - {task_name}")


if __name__ == "__main__":
    main()

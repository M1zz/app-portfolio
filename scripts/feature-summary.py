#!/usr/bin/env python3
"""
전체 앱의 feature 통계 요약
"""

import json
from pathlib import Path

APPS_DIR = Path("/Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO/Data/apps")


def main():
    """메인 실행"""
    print("=" * 80)
    print("전체 Feature 통계")
    print("=" * 80)
    print()

    app_files = sorted(APPS_DIR.glob("*.json"))

    total_features = 0
    apps_with_features = 0
    feature_breakdown = {}

    for app_file in app_files:
        with open(app_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        app_name = data.get('name', app_file.stem)
        all_tasks = data.get('allTasks', [])

        # feature 태스크 찾기
        features = []
        for task in all_tasks:
            has_feature_label = 'labels' in task and 'feature' in task.get('labels', [])
            has_feature_meta = 'featureMetadata' in task and task['featureMetadata']

            if has_feature_label or has_feature_meta:
                features.append(task)
                category = task.get('featureMetadata', {}).get('category', '기타')
                feature_breakdown[category] = feature_breakdown.get(category, 0) + 1

        if features:
            apps_with_features += 1
            total_features += len(features)
            print(f"{app_name}: {len(features)}개 feature")

    print()
    print("=" * 80)
    print(f"총 {apps_with_features}개 앱, {total_features}개 feature")
    print()
    print("카테고리별 분포:")
    for category, count in sorted(feature_breakdown.items(), key=lambda x: -x[1]):
        print(f"  {category}: {count}개")
    print("=" * 80)


if __name__ == "__main__":
    main()

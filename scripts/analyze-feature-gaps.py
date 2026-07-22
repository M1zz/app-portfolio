#!/usr/bin/env python3
"""
각 앱의 feature 개수 분석 및 부족한 앱 식별
"""

import json
from pathlib import Path

APPS_DIR = Path("/Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO/Data/apps")


def main():
    """메인 실행"""
    print("=" * 80)
    print("Feature 개수 분석")
    print("=" * 80)
    print()

    app_files = sorted(APPS_DIR.glob("*.json"))
    app_feature_counts = []

    for app_file in app_files:
        with open(app_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        app_name = data.get('name', app_file.stem)
        all_tasks = data.get('allTasks', [])

        feature_count = 0
        non_feature_count = 0

        for task in all_tasks:
            has_feature = 'featureMetadata' in task and task['featureMetadata']
            if has_feature:
                feature_count += 1
            else:
                non_feature_count += 1

        app_feature_counts.append({
            'name': app_name,
            'id': app_file.stem,
            'features': feature_count,
            'non_features': non_feature_count,
            'total': len(all_tasks)
        })

    # 정렬: feature 개수 기준
    app_feature_counts.sort(key=lambda x: x['features'])

    print("📊 앱별 Feature 개수 (적은 순)")
    print("-" * 80)
    for app in app_feature_counts:
        bar = "█" * app['features']
        print(f"{app['name']:20s} {app['features']:2d}개 feature, {app['non_features']:2d}개 일반 태스크 {bar}")

    print()
    print("=" * 80)
    print("⚠️  보강이 필요한 앱 (5개 이하)")
    print("=" * 80)
    for app in app_feature_counts:
        if app['features'] <= 5:
            print(f"  • {app['name']} ({app['id']}): {app['features']}개")

    print()
    print("=" * 80)
    print("✨ 목표: 모든 앱을 클립키보드 수준(10개 이상)으로")
    print("=" * 80)


if __name__ == "__main__":
    main()

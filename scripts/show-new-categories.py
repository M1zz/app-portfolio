#!/usr/bin/env python3
"""
재분류된 카테고리 통계 보기
"""

import json
from pathlib import Path
from collections import Counter

APPS_DIR = Path("/Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO/Data/apps")


def main():
    """메인 실행"""
    print("=" * 80)
    print("20년차 기획자 관점 - 새로운 Feature 카테고리")
    print("=" * 80)
    print()

    app_files = sorted(APPS_DIR.glob("*.json"))

    all_categories = []
    app_categories = {}

    for app_file in app_files:
        with open(app_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        app_name = data.get('name', app_file.stem)
        categories = []

        for task in data.get('allTasks', []):
            if 'featureMetadata' in task and task['featureMetadata']:
                category = task['featureMetadata'].get('category', '기타')
                all_categories.append(category)
                categories.append(category)

        if categories:
            app_categories[app_name] = list(set(categories))

    print("📊 앱별 카테고리 분포")
    print("-" * 80)
    for app_name, categories in sorted(app_categories.items()):
        print(f"\n{app_name}:")
        for cat in sorted(categories):
            print(f"  • {cat}")

    print("\n" + "=" * 80)
    print("📈 전체 카테고리 사용 빈도")
    print("=" * 80)
    print()

    category_counts = Counter(all_categories)
    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"{category:30s} {count:3d}개")

    print()
    print("=" * 80)
    print(f"총 {len(category_counts)}개의 고유 카테고리")
    print(f"총 {sum(category_counts.values())}개 feature")
    print("=" * 80)
    print()
    print("✨ 변화:")
    print("  기존: 핵심기능, UI/UX, 데이터, 통합 등 추상적 분류")
    print("  현재: 빠른 입력, 기기 간 연동, 절약 시간 확인 등 사용자 중심 분류")
    print()


if __name__ == "__main__":
    main()

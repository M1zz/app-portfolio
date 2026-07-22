#!/usr/bin/env python3
"""
마지막 남은 feature들 추가
"""

import json
from pathlib import Path

APPS_DIR = Path("/Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO/Data/apps")

FINAL_FEATURES = {
    "bucket-climb": {
        "앱 로딩 성능 최적화": {
            "category": "성능",
            "description": "앱 시작 속도와 데이터 로딩 속도를 개선합니다",
            "userValue": "앱을 열자마자 빠르게 버킷리스트를 확인하고 작업할 수 있습니다",
            "technicalNotes": "이미지 캐싱, 지연 로딩, 데이터베이스 최적화"
        }
    },
    "life-restaurant": {
        "도형 은 절반으로 보여야지": {
            "category": "UI/UX",
            "description": "맛집 평점을 반쪽 별점으로 세밀하게 표현할 수 있습니다",
            "userValue": "3.5점, 4.5점 등 더 정확한 평가를 할 수 있습니다",
            "technicalNotes": "반쪽 별 아이콘, 소수점 평점"
        }
    },
    "ecdesigner": {
        "마일스톤 > EC 계층 구조": {
            "category": "핵심기능",
            "description": "프로젝트를 마일스톤과 작업으로 계층적으로 관리할 수 있습니다",
            "userValue": "복잡한 프로젝트를 단계별로 나누어 체계적으로 진행할 수 있습니다",
            "technicalNotes": "트리 구조, 계층형 데이터 모델"
        }
    }
}


def load_app_json(app_file):
    """앱 JSON 파일 로드"""
    with open(app_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_app_json(app_file, data):
    """앱 JSON 파일 저장"""
    with open(app_file, 'r', encoding='utf-8') as f:
        original = f.read()

    # 백업
    backup_file = app_file.with_suffix('.json.backup4')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original)

    # 저장
    with open(app_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_final_features(app_file):
    """마지막 feature 추가"""
    app_id = app_file.stem
    data = load_app_json(app_file)

    if app_id not in FINAL_FEATURES:
        return 0

    features_map = FINAL_FEATURES[app_id]
    updated_count = 0

    for task in data.get('allTasks', []):
        task_name = task['name']

        if 'featureMetadata' in task and task['featureMetadata']:
            continue

        if task_name in features_map:
            if 'labels' not in task:
                task['labels'] = []
            if 'feature' not in task['labels']:
                task['labels'].append('feature')

            task['featureMetadata'] = features_map[task_name]
            updated_count += 1

    if updated_count > 0:
        save_app_json(app_file, data)
        print(f"✅ {data.get('name', app_id)}: {updated_count}개 feature 추가")
        return updated_count
    else:
        return 0


def main():
    """메인 실행"""
    print("=" * 80)
    print("마지막 Feature 정보 추가")
    print("=" * 80)
    print()

    app_files = sorted(APPS_DIR.glob("*.json"))
    total_updated = 0

    for app_file in app_files:
        count = add_final_features(app_file)
        total_updated += count

    print()
    print("=" * 80)
    print(f"총 {total_updated}개 feature 추가 완료")
    print("=" * 80)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
피처 수집 스크립트
각 앱의 태스크를 분석하여 피처로 분류하고 메타데이터를 추가합니다.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

# 피처로 간주할 키워드 패턴
FEATURE_KEYWORDS = [
    # 핵심 기능
    r'기능', r'추가', r'구현', r'지원', r'제공', r'관리',
    # 기술적 특징
    r'동기화', r'백업', r'복원', r'저장', r'불러오기',
    # UI/UX
    r'디자인', r'화면', r'뷰', r'UI', r'레이아웃', r'테마',
    # 통합/연동
    r'연동', r'통합', r'공유', r'내보내기', r'가져오기',
    # 보안
    r'보안', r'인증', r'암호화', r'잠금', r'Face', r'Touch',
]

# 제외할 패턴 (운영/마케팅 관련)
EXCLUDE_KEYWORDS = [
    r'배포', r'출시', r'스토어', r'영상', r'리뷰', r'광고', r'마케팅',
    r'인스타', r'링크드인', r'블로그', r'홍보', r'테스트플라이트',
    r'심사', r'제출', r'승인', r'거절'
]

# 카테고리 분류 키워드
CATEGORY_KEYWORDS = {
    "핵심기능": [
        r'기능', r'작성', r'생성', r'만들기', r'추가', r'등록', r'입력',
        r'편집', r'수정', r'삭제', r'관리', r'조회', r'검색', r'필터'
    ],
    "보안": [
        r'보안', r'인증', r'암호화', r'잠금', r'Face', r'Touch', r'비밀번호',
        r'프라이버시', r'권한', r'접근', r'민감'
    ],
    "커스터마이징": [
        r'설정', r'커스텀', r'개인화', r'맞춤', r'테마', r'색상', r'폰트',
        r'크기', r'레이아웃', r'배치', r'조정', r'변경'
    ],
    "통합": [
        r'동기화', r'클라우드', r'iCloud', r'공유', r'내보내기', r'가져오기',
        r'연동', r'통합', r'API', r'캘린더', r'사진', r'연락처'
    ],
    "UI/UX": [
        r'디자인', r'UI', r'UX', r'화면', r'뷰', r'인터페이스', r'애니메이션',
        r'전환', r'네비게이션', r'탭', r'버튼', r'아이콘'
    ],
    "성능": [
        r'최적화', r'성능', r'속도', r'빠르', r'효율', r'메모리', r'배터리',
        r'용량', r'로딩', r'캐시'
    ],
    "데이터": [
        r'백업', r'복원', r'저장', r'불러오기', r'데이터', r'히스토리',
        r'기록', r'로그', r'통계', r'분석'
    ]
}


def is_feature_task(task_name: str) -> bool:
    """태스크가 피처인지 판단"""
    # 제외 키워드 체크
    for pattern in EXCLUDE_KEYWORDS:
        if re.search(pattern, task_name, re.IGNORECASE):
            return False

    # 피처 키워드 체크
    for pattern in FEATURE_KEYWORDS:
        if re.search(pattern, task_name, re.IGNORECASE):
            return True

    return False


def categorize_feature(task_name: str) -> str:
    """피처의 카테고리 추천"""
    scores = {}

    for category, patterns in CATEGORY_KEYWORDS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, task_name, re.IGNORECASE):
                score += 1
        if score > 0:
            scores[category] = score

    if scores:
        # 가장 높은 점수의 카테고리 반환
        return max(scores, key=scores.get)

    return "기타"


def generate_feature_description(task_name: str, category: str) -> str:
    """피처 설명 생성"""
    # 간단한 템플릿 기반 설명
    if "추가" in task_name or "구현" in task_name:
        return f"{task_name}을 통해 사용자에게 새로운 기능을 제공합니다"
    elif "개선" in task_name or "최적화" in task_name:
        return f"{task_name}하여 사용자 경험을 향상시킵니다"
    elif "지원" in task_name:
        return f"{task_name}을 통해 더 나은 사용성을 제공합니다"
    else:
        return f"{category} 관련 기능: {task_name}"


def generate_user_value(category: str) -> str:
    """사용자 가치 생성"""
    value_map = {
        "핵심기능": "앱의 주요 기능을 활용하여 목표를 효율적으로 달성",
        "보안": "개인 정보를 안전하게 보호하고 프라이버시 유지",
        "커스터마이징": "개인의 취향과 필요에 맞게 앱을 맞춤 설정",
        "통합": "다른 기기나 서비스와 연동하여 편리하게 사용",
        "UI/UX": "직관적이고 아름다운 인터페이스로 즐거운 사용 경험",
        "성능": "빠르고 효율적인 동작으로 시간 절약",
        "데이터": "중요한 데이터를 안전하게 보관하고 관리",
    }
    return value_map.get(category, "앱 사용 경험 향상")


def process_app_file(file_path: Path) -> Dict:
    """앱 JSON 파일 처리"""
    print(f"\n처리 중: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    app_name = data.get('name', file_path.stem)
    all_tasks = data.get('allTasks', [])

    if not all_tasks:
        print(f"  ⚠️  태스크가 없습니다")
        return data

    feature_count = 0
    updated_tasks = []

    for task in all_tasks:
        task_name = task.get('name', '')

        # 이미 feature 라벨이 있으면 스킵
        labels = task.get('labels', [])
        if labels and 'feature' in labels:
            updated_tasks.append(task)
            feature_count += 1
            continue

        # 피처로 판단되면 메타데이터 추가
        if is_feature_task(task_name):
            category = categorize_feature(task_name)

            # labels 추가
            if not labels:
                task['labels'] = ['feature']
            elif 'feature' not in labels:
                task['labels'].append('feature')

            # featureMetadata 추가
            if 'featureMetadata' not in task:
                task['featureMetadata'] = {
                    'category': category,
                    'description': generate_feature_description(task_name, category),
                    'userValue': generate_user_value(category),
                    'technicalNotes': None
                }

            feature_count += 1
            print(f"  ✓ {task_name} → [{category}]")

        updated_tasks.append(task)

    data['allTasks'] = updated_tasks

    # stats에 todo 필드 추가 (없으면)
    if 'stats' in data:
        stats = data['stats']
        if 'todo' not in stats:
            stats['todo'] = 0

    print(f"  📊 총 {len(all_tasks)}개 태스크 중 {feature_count}개 피처 발견")

    return data


def main():
    """메인 함수"""
    # 앱 데이터 폴더 경로
    apps_dir = Path(__file__).parent.parent / 'projects/PortfolioCEO/PortfolioCEO/Data/apps'

    if not apps_dir.exists():
        print(f"❌ 앱 데이터 폴더를 찾을 수 없습니다: {apps_dir}")
        return

    print(f"📁 앱 데이터 폴더: {apps_dir}")
    print("=" * 60)

    # 모든 JSON 파일 처리
    json_files = sorted(apps_dir.glob('*.json'))
    total_apps = len(json_files)

    for i, json_file in enumerate(json_files, 1):
        print(f"\n[{i}/{total_apps}] {json_file.stem}")

        try:
            updated_data = process_app_file(json_file)

            # 백업 생성
            backup_path = json_file.with_suffix('.json.backup')
            if not backup_path.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    with open(backup_path, 'w', encoding='utf-8') as bf:
                        bf.write(f.read())

            # 업데이트된 데이터 저장
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=2)

            print(f"  ✅ 저장 완료")

        except Exception as e:
            print(f"  ❌ 오류: {e}")

    print("\n" + "=" * 60)
    print("✨ 피처 수집 완료!")
    print(f"💡 백업 파일: *.json.backup")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
upgrade-apps-to-clipkeyboard-level.py에서 추가한 feature들을
recategorize-features.py의 FEATURE_RECATEGORIZATION에 추가
"""

import json
from pathlib import Path

# 이미 recategorize-features.py에 있는 feature들은 제외하고
# 새로 추가한 feature만 출력

APPS_DIR = Path("/Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO/Data/apps")

# 각 앱별로 확인
APPS_TO_CHECK = {
    "cooltime": "쿨타임",
    "probability-calculator": "확률계산기",
    "rebound-journal": "리바운드 저널",
    "relax-on": "릴렉스 온",
    "shared-day-designer": "휴가 플래너",
    "bami-log": "바미로그",
    "daily-compliment": "오늘의 주접",
    "donkko-mart": "돈꼬마트",
    "pixel-mimi": "픽셀 미미",
    "quiz": "퀴즈",
    "schedule-assistant": "일정비서"
}

def extract_features_from_app(app_id):
    """앱에서 feature 메타데이터가 있는 작업들을 추출"""
    app_file = APPS_DIR / f"{app_id}.json"

    with open(app_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    features = []
    for task in data.get('allTasks', []):
        if 'featureMetadata' in task and task['featureMetadata']:
            meta = task['featureMetadata']
            # usageScenario, problemSolved, userBenefit가 있으면
            if all(k in meta for k in ['usageScenario', 'problemSolved', 'userBenefit']):
                features.append({
                    'name': task['name'],
                    'category': meta.get('category', ''),
                    'usageScenario': meta.get('usageScenario', ''),
                    'problemSolved': meta.get('problemSolved', ''),
                    'userBenefit': meta.get('userBenefit', '')
                })

    return features

def generate_python_dict(app_id, features):
    """Python dictionary 형식으로 출력"""
    lines = [f'    "{app_id}": {{']

    for feature in features:
        name = feature['name']
        category = feature['category']
        usage = feature['usageScenario']
        problem = feature['problemSolved']
        benefit = feature['userBenefit']

        lines.append(f'        "{name}": {{')
        lines.append(f'            "category": "{category}",')
        lines.append(f'            "usageScenario": "{usage}",')
        lines.append(f'            "problemSolved": "{problem}",')
        lines.append(f'            "userBenefit": "{benefit}"')
        lines.append('        },')

    # 마지막 콤마 제거
    if lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]

    lines.append('    },')
    lines.append('')

    return '\n'.join(lines)

def main():
    print("새로 추가된 feature들을 recategorize-features.py 형식으로 출력")
    print()
    print("# recategorize-features.py의 FEATURE_RECATEGORIZATION에 추가할 내용:")
    print()

    for app_id, app_name in APPS_TO_CHECK.items():
        features = extract_features_from_app(app_id)
        if features:
            print(f"    # {app_name} - {len(features)}개 features")
            print(generate_python_dict(app_id, features))

if __name__ == "__main__":
    main()

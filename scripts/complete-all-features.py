#!/usr/bin/env python3
"""
모든 앱의 태스크를 분석하여 feature 정보를 완성하는 스크립트
"""

import json
from pathlib import Path

APPS_DIR = Path("/Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO/Data/apps")

# 각 앱별 태스크의 feature 메타데이터
# 태스크 이름을 키로, feature 정보를 값으로
COMPLETE_FEATURES = {
    "clip-keyboard": {
        "템플릿 관리 개선": {
            "category": "UI/UX",
            "description": "템플릿을 더 쉽게 추가, 수정, 삭제할 수 있도록 UI를 개선합니다",
            "userValue": "템플릿 관리가 직관적이어서 자주 쓰는 텍스트를 빠르게 정리할 수 있습니다",
            "technicalNotes": "SwiftUI 리스트, 스와이프 액션"
        },
        "통계 대시보드": {
            "category": "데이터",
            "description": "저장한 시간, 사용 빈도 등의 통계를 시각화하여 보여줍니다",
            "userValue": "얼마나 시간을 절약했는지 한눈에 확인하며 성취감을 느낄 수 있습니다",
            "technicalNotes": "Charts 프레임워크, 데이터 집계"
        },
        "위젯 지원": {
            "category": "핵심기능",
            "description": "홈 화면 위젯에서 자주 쓰는 템플릿을 바로 복사할 수 있습니다",
            "userValue": "앱을 열지 않고도 위젯에서 바로 템플릿을 사용할 수 있습니다",
            "technicalNotes": "WidgetKit, App Intent"
        }
    },

    "shared-day-designer": {
        "일정 색상 커스터마이징": {
            "category": "커스터마이징",
            "description": "각 일정이나 카테고리별로 원하는 색상을 지정할 수 있습니다",
            "userValue": "일정을 색상으로 구분하여 한눈에 파악할 수 있습니다",
            "technicalNotes": "컬러 피커, 사용자 설정 저장"
        },
        "반복 일정 설정": {
            "category": "핵심기능",
            "description": "매주, 매월 반복되는 일정을 쉽게 등록할 수 있습니다",
            "userValue": "반복되는 일정을 매번 입력하지 않아도 자동으로 생성됩니다",
            "technicalNotes": "반복 규칙 파싱, 일정 생성 알고리즘"
        },
        "가족 구성원 역할 설정": {
            "category": "핵심기능",
            "description": "각 가족 구성원에게 역할을 부여하고 담당 일정을 배정할 수 있습니다",
            "userValue": "누가 무엇을 담당하는지 명확히 하여 가족 협업이 원활해집니다",
            "technicalNotes": "사용자 그룹 관리, 권한 시스템"
        },
        "알림 커스터마이징": {
            "category": "커스터마이징",
            "description": "일정별로 알림 시간과 방식을 자유롭게 설정할 수 있습니다",
            "userValue": "중요한 일정은 미리 알림받고, 덜 중요한 일정은 알림을 끌 수 있습니다",
            "technicalNotes": "로컬 알림, 알림 스케줄링"
        }
    },

    "life-restaurant": {
        "맛집 카테고리 필터": {
            "category": "UI/UX",
            "description": "한식, 양식, 일식 등 음식 종류별로 맛집을 필터링할 수 있습니다",
            "userValue": "먹고 싶은 음식 종류에 따라 방문했던 맛집을 빠르게 찾을 수 있습니다",
            "technicalNotes": "카테고리 태그, 필터링 로직"
        },
        "재방문 의사 표시": {
            "category": "핵심기능",
            "description": "방문한 식당에 대해 다시 가고 싶은지 여부를 표시할 수 있습니다",
            "userValue": "좋았던 식당과 별로였던 식당을 구분하여 더 나은 선택을 할 수 있습니다",
            "technicalNotes": "boolean 플래그, 리스트 정렬"
        },
        "친구와 공유": {
            "category": "통합",
            "description": "맛집 정보를 친구에게 메시지나 SNS로 공유할 수 있습니다",
            "userValue": "친구에게 맛집을 추천할 때 사진과 평가를 함께 전달할 수 있습니다",
            "technicalNotes": "UIActivityViewController, 공유 시트"
        }
    },

    "pixel-mimi": {
        "레이어 시스템": {
            "category": "핵심기능",
            "description": "여러 레이어를 만들어 복잡한 픽셀 아트를 그릴 수 있습니다",
            "userValue": "배경과 전경을 분리하여 더 정교한 작품을 만들 수 있습니다",
            "technicalNotes": "레이어 관리, 블렌딩 모드"
        },
        "도구 모음": {
            "category": "핵심기능",
            "description": "펜, 지우개, 채우기, 선 그리기 등 다양한 도구를 사용할 수 있습니다",
            "userValue": "상황에 맞는 도구로 더 효율적으로 그림을 그릴 수 있습니다",
            "technicalNotes": "그리기 알고리즘, 도구 상태 관리"
        },
        "갤러리": {
            "category": "데이터",
            "description": "완성한 픽셀 아트를 갤러리에 저장하고 관리할 수 있습니다",
            "userValue": "작품을 모아두고 나중에 다시 보거나 수정할 수 있습니다",
            "technicalNotes": "파일 저장, 썸네일 생성"
        }
    },

    "probability-calculator": {
        "조합 계산기": {
            "category": "핵심기능",
            "description": "nCr (조합) 계산을 수행하고 결과를 표시합니다",
            "userValue": "복잡한 조합 공식을 외우지 않고 빠르게 계산할 수 있습니다",
            "technicalNotes": "조합 알고리즘, 큰 수 처리"
        },
        "순열 계산기": {
            "category": "핵심기능",
            "description": "nPr (순열) 계산을 수행하고 결과를 표시합니다",
            "userValue": "순서가 중요한 경우의 수를 쉽게 계산할 수 있습니다",
            "technicalNotes": "순열 알고리즘, 팩토리얼 계산"
        },
        "조건부 확률": {
            "category": "핵심기능",
            "description": "조건부 확률 P(A|B)를 계산할 수 있습니다",
            "userValue": "특정 조건 하에서의 확률을 정확히 파악할 수 있습니다",
            "technicalNotes": "베이즈 정리, 확률 계산"
        }
    },

    "quiz": {
        "타이머 기능": {
            "category": "핵심기능",
            "description": "퀴즈 풀이에 제한 시간을 설정할 수 있습니다",
            "userValue": "시간 제한으로 긴장감 있는 퀴즈 경험을 할 수 있습니다",
            "technicalNotes": "카운트다운 타이머, 시간 초과 처리"
        },
        "난이도 선택": {
            "category": "핵심기능",
            "description": "쉬움, 보통, 어려움 등 난이도를 선택할 수 있습니다",
            "userValue": "자신의 수준에 맞는 퀴즈를 풀며 성취감을 느낄 수 있습니다",
            "technicalNotes": "난이도 필터링, 퀴즈 분류"
        },
        "리더보드": {
            "category": "데이터",
            "description": "높은 점수를 기록한 사용자들의 순위를 보여줍니다",
            "userValue": "다른 사용자와 경쟁하며 동기부여를 얻을 수 있습니다",
            "technicalNotes": "점수 저장, 순위 정렬"
        }
    },

    "rainbow-of-desire": {
        "감정 분석": {
            "category": "데이터",
            "description": "기록한 감정 데이터를 분석하여 인사이트를 제공합니다",
            "userValue": "어떤 상황에서 어떤 감정을 느끼는지 패턴을 발견할 수 있습니다",
            "technicalNotes": "데이터 분석, 패턴 인식"
        },
        "감정 일기": {
            "category": "핵심기능",
            "description": "색상과 함께 구체적인 감정 일기를 작성할 수 있습니다",
            "userValue": "감정을 더 깊이 탐구하고 자기 이해를 높일 수 있습니다",
            "technicalNotes": "텍스트 에디터, 감정 태그"
        }
    },

    "rebound-journal": {
        "목표 설정": {
            "category": "핵심기능",
            "description": "회복 과정에서 달성하고 싶은 목표를 설정할 수 있습니다",
            "userValue": "명확한 목표를 가지고 회복 여정을 진행할 수 있습니다",
            "technicalNotes": "목표 관리, 진행률 추적"
        },
        "긍정 확언": {
            "category": "핵심기능",
            "description": "매일 긍정적인 확언 문구를 받아볼 수 있습니다",
            "userValue": "긍정적인 메시지로 힘을 얻고 희망을 가질 수 있습니다",
            "technicalNotes": "확언 DB, 알림 시스템"
        },
        "안전 공간": {
            "category": "보안",
            "description": "일기를 암호나 생체인증으로 보호할 수 있습니다",
            "userValue": "개인적인 감정을 안전하게 기록할 수 있습니다",
            "technicalNotes": "LocalAuthentication, 데이터 암호화"
        }
    },

    "relax-on": {
        "즐겨찾기": {
            "category": "커스터마이징",
            "description": "자주 듣는 소리 조합을 즐겨찾기에 저장할 수 있습니다",
            "userValue": "매번 소리를 선택하지 않고 바로 재생할 수 있습니다",
            "technicalNotes": "프리셋 저장, 빠른 실행"
        },
        "타이머": {
            "category": "핵심기능",
            "description": "일정 시간 후 자동으로 소리가 꺼지도록 설정할 수 있습니다",
            "userValue": "수면 전에 사용할 때 자동으로 꺼져서 편리합니다",
            "technicalNotes": "슬립 타이머, 페이드 아웃"
        },
        "명상 가이드": {
            "category": "핵심기능",
            "description": "음성 가이드와 함께 명상을 진행할 수 있습니다",
            "userValue": "초보자도 쉽게 명상을 배우고 실천할 수 있습니다",
            "technicalNotes": "음성 녹음, 가이드 스크립트"
        }
    },

    "schedule-assistant": {
        "시간 블록킹": {
            "category": "핵심기능",
            "description": "하루를 시간 블록으로 나누어 작업을 배정할 수 있습니다",
            "userValue": "하루를 체계적으로 관리하며 생산성을 높일 수 있습니다",
            "technicalNotes": "시간 블록 UI, 드래그 앤 드롭"
        },
        "작업 우선순위": {
            "category": "핵심기능",
            "description": "작업의 중요도와 긴급도를 설정하여 우선순위를 정할 수 있습니다",
            "userValue": "중요한 일을 먼저 처리하며 효율적으로 일할 수 있습니다",
            "technicalNotes": "아이젠하워 매트릭스, 자동 정렬"
        }
    },

    "ecdesigner": {
        "QR 코드 생성": {
            "category": "핵심기능",
            "description": "명함에 QR 코드를 추가하여 연락처를 쉽게 공유할 수 있습니다",
            "userValue": "상대방이 QR 코드를 스캔하여 바로 연락처를 저장할 수 있습니다",
            "technicalNotes": "QR 코드 생성 라이브러리"
        },
        "인쇄 설정": {
            "category": "UI/UX",
            "description": "명함 크기, 해상도 등 인쇄 옵션을 설정할 수 있습니다",
            "userValue": "인쇄소에 맞는 형식으로 파일을 생성할 수 있습니다",
            "technicalNotes": "PDF 생성, DPI 설정"
        }
    },

    "double-reminder": {
        "스누즈 기능": {
            "category": "핵심기능",
            "description": "알림을 일정 시간 미루기 할 수 있습니다",
            "userValue": "지금 당장 할 수 없을 때 잠시 미뤄두었다가 다시 알림받을 수 있습니다",
            "technicalNotes": "알림 재스케줄링, 스누즈 옵션"
        },
        "위치 기반 알림": {
            "category": "핵심기능",
            "description": "특정 장소에 도착하거나 떠날 때 알림을 받을 수 있습니다",
            "userValue": "시간이 아닌 위치로 알림받아 더 적절한 타이밍에 확인할 수 있습니다",
            "technicalNotes": "CoreLocation, 지오펜싱"
        }
    },

    "bami-log": {
        "진통기록 + 호흡을 도와주는 것 추가": {
            "category": "핵심기능",
            "description": "진통 시간을 기록하고 호흡법을 안내받을 수 있습니다",
            "userValue": "출산 과정에서 진통 간격을 정확히 측정하고 호흡을 조절하는데 도움을 받습니다",
            "technicalNotes": "타이머 기능, 호흡 가이드 애니메이션"
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
    backup_file = app_file.with_suffix('.json.backup2')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original)

    # 저장
    with open(app_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def should_be_feature(task_name):
    """태스크가 feature로 분류될 수 있는지 판단"""
    # 제외할 패턴
    exclude_patterns = [
        "배포", "출시", "릴리즈",
        "버그", "BUG", "수정",
        "앱 구상", "기획",
        "사용성 개선", "개선",
        "리팩토링", "refactor"
    ]

    for pattern in exclude_patterns:
        if pattern in task_name:
            return False

    return True


def complete_features(app_file):
    """앱의 feature 정보 완성"""
    app_id = app_file.stem
    data = load_app_json(app_file)

    updated_count = 0

    # 앱별 feature 정보가 있는 경우
    if app_id in COMPLETE_FEATURES:
        features_map = COMPLETE_FEATURES[app_id]

        for task in data.get('allTasks', []):
            task_name = task['name']

            # 이미 feature 메타데이터가 있으면 스킵
            if 'featureMetadata' in task and task['featureMetadata']:
                continue

            # feature 정보가 있는 경우 추가
            if task_name in features_map:
                # labels 추가
                if 'labels' not in task:
                    task['labels'] = []
                if 'feature' not in task['labels']:
                    task['labels'].append('feature')

                # featureMetadata 추가
                task['featureMetadata'] = features_map[task_name]
                updated_count += 1

    # 저장
    if updated_count > 0:
        save_app_json(app_file, data)
        print(f"✅ {data.get('name', app_id)}: {updated_count}개 feature 완성")
        return True
    else:
        print(f"⚪ {data.get('name', app_id)}: 업데이트 없음")
        return False


def main():
    """메인 실행"""
    print("=" * 60)
    print("Feature 정보 완성")
    print("=" * 60)
    print()

    app_files = sorted(APPS_DIR.glob("*.json"))

    updated = 0

    for app_file in app_files:
        if complete_features(app_file):
            updated += 1

    print()
    print("=" * 60)
    print(f"완료: {updated}개 앱 업데이트")
    print("=" * 60)


if __name__ == "__main__":
    main()

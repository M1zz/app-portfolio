#!/usr/bin/env python3
"""
모든 앱의 실제 태스크를 feature로 완성하는 스크립트
"""

import json
from pathlib import Path

APPS_DIR = Path("/Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO/Data/apps")

# 각 앱의 실제 태스크 이름에 맞춘 feature 메타데이터
TASK_FEATURES = {
    "bucket-climb": {
        "기본 버킷리스트 CRUD": {
            "category": "핵심기능",
            "description": "버킷리스트를 추가, 수정, 삭제, 완료 처리할 수 있습니다",
            "userValue": "꿈과 목표를 자유롭게 관리하며 달성해나갈 수 있습니다",
            "technicalNotes": "SwiftData CRUD, 상태 관리"
        },
        "카테고리 시스템 개선": {
            "category": "UI/UX",
            "description": "버킷리스트를 여행, 취미, 경력 등 카테고리별로 분류할 수 있습니다",
            "userValue": "목표를 분야별로 정리하여 균형잡힌 삶을 계획할 수 있습니다",
            "technicalNotes": "카테고리 필터, 아이콘 시스템"
        },
        "위젯 랜덤 버킷리스트 표시": {
            "category": "핵심기능",
            "description": "홈 화면 위젯에서 랜덤한 버킷리스트를 보여줍니다",
            "userValue": "하루에 한 번씩 다른 꿈을 상기하며 동기부여를 받을 수 있습니다",
            "technicalNotes": "WidgetKit, 랜덤 선택 알고리즘"
        },
        "통계 대시보드": {
            "category": "데이터",
            "description": "달성한 버킷리스트, 진행 중인 목표 등의 통계를 보여줍니다",
            "userValue": "자신의 성취를 확인하며 지속적인 동기부여를 얻을 수 있습니다",
            "technicalNotes": "차트 라이브러리, 데이터 집계"
        }
    },

    "clip-keyboard": {
        "맥 OS에서 동작하게 하기": {
            "category": "플랫폼",
            "description": "macOS에서도 클립키보드를 사용할 수 있습니다",
            "userValue": "iOS와 Mac을 넘나들며 일관된 템플릿 사용 경험을 할 수 있습니다",
            "technicalNotes": "AppKit, Catalyst, iCloud 동기화"
        },
        "붙여넣기 안내 설정 도와주기": {
            "category": "UI/UX",
            "description": "키보드 붙여넣기 권한 설정 방법을 친절하게 안내합니다",
            "userValue": "처음 사용하는 사람도 쉽게 설정하고 바로 사용할 수 있습니다",
            "technicalNotes": "온보딩 플로우, 애니메이션 가이드"
        },
        "키보드 표시명 중복 제거": {
            "category": "UI/UX",
            "description": "키보드 설정에서 중복 표시명이 나타나지 않도록 개선합니다",
            "userValue": "깔끔한 UI로 혼란 없이 키보드를 사용할 수 있습니다",
            "technicalNotes": "키보드 익스텐션 메타데이터"
        }
    },

    "double-reminder": {
        "예비알림 마크 개선": {
            "category": "UI/UX",
            "description": "예비 알림이 설정되어 있음을 시각적으로 명확히 표시합니다",
            "userValue": "어떤 알림에 예비가 설정되어 있는지 한눈에 파악할 수 있습니다",
            "technicalNotes": "배지, 아이콘 인디케이터"
        },
        "온보딩 개선": {
            "category": "UI/UX",
            "description": "앱 첫 사용 시 이중 알림의 장점을 명확히 설명합니다",
            "userValue": "앱의 핵심 가치를 빠르게 이해하고 바로 활용할 수 있습니다",
            "technicalNotes": "페이지 인디케이터, 인터랙티브 가이드"
        },
        "각각 알림마다 노티 레이블 넣기": {
            "category": "핵심기능",
            "description": "첫 번째/두 번째 알림을 구분할 수 있는 레이블을 표시합니다",
            "userValue": "알림을 받았을 때 지금이 첫 번째인지 마지막 알림인지 바로 알 수 있습니다",
            "technicalNotes": "알림 콘텐츠 커스터마이징"
        },
        "다음 알림까지 남은 시간 보여주기": {
            "category": "UI/UX",
            "description": "예정된 알림까지 남은 시간을 실시간으로 표시합니다",
            "userValue": "다음 알림 시간을 예측하고 준비할 수 있습니다",
            "technicalNotes": "타이머, 실시간 업데이트"
        },
        "사용자가 사용했던 타이머의 기록 남기기와 빠른 타이머 그리고 그 레이블링": {
            "category": "커스터마이징",
            "description": "자주 쓰는 알림 시간을 저장하고 빠르게 재사용할 수 있습니다",
            "userValue": "매번 시간을 설정하지 않고 자주 쓰는 패턴을 빠르게 선택할 수 있습니다",
            "technicalNotes": "히스토리 저장, 퀵 액션"
        },
        "접근성 개선": {
            "category": "접근성",
            "description": "VoiceOver, 다이나믹 타입 등 접근성 기능을 지원합니다",
            "userValue": "시각 장애가 있어도 불편함 없이 앱을 사용할 수 있습니다",
            "technicalNotes": "VoiceOver 레이블, 다이나믹 폰트"
        },
        "권한 거부 되었을 때 다시 하는 법 혹은 부작용 안내": {
            "category": "UI/UX",
            "description": "알림 권한이 없을 때 설정 방법을 안내하고 영향을 설명합니다",
            "userValue": "권한 문제로 앱을 못 쓰는 상황을 쉽게 해결할 수 있습니다",
            "technicalNotes": "권한 체크, 설정 앱 딥링크"
        },
        "사용자 사운드 커스터마이징": {
            "category": "커스터마이징",
            "description": "알림음을 개인 취향에 맞게 선택할 수 있습니다",
            "userValue": "좋아하는 소리로 알림을 받아 더 쾌적한 경험을 할 수 있습니다",
            "technicalNotes": "사운드 피커, 커스텀 오디오"
        }
    },

    "ecdesigner": {
        "사이드바-캔버스 분리": {
            "category": "UI/UX",
            "description": "편집 도구와 캔버스를 명확히 분리하여 작업 공간을 넓힙니다",
            "userValue": "더 넓은 캔버스에서 명함을 디자인할 수 있습니다",
            "technicalNotes": "레이아웃 시스템, 반응형 UI"
        },
        "Tips 영역 하단 분리": {
            "category": "UI/UX",
            "description": "디자인 팁과 가이드를 하단에 따로 표시합니다",
            "userValue": "필요할 때만 팁을 확인하며 작업에 집중할 수 있습니다",
            "technicalNotes": "접이식 패널, 툴팁"
        },
        "흰 배경 + 스냅그리드": {
            "category": "핵심기능",
            "description": "요소를 배치할 때 그리드에 자동으로 정렬됩니다",
            "userValue": "정확하게 정렬된 전문적인 명함을 쉽게 만들 수 있습니다",
            "technicalNotes": "그리드 시스템, 스냅 알고리즘"
        },
        "헤더 아이콘 정리 (엘립시스 메뉴)": {
            "category": "UI/UX",
            "description": "자주 쓰지 않는 기능을 메뉴로 정리하여 UI를 깔끔하게 합니다",
            "userValue": "핵심 기능에 집중하며 깔끔한 인터페이스를 사용할 수 있습니다",
            "technicalNotes": "메뉴 UI, 액션 그룹핑"
        },
        "사이드바 단순화 (우클릭 메뉴)": {
            "category": "UI/UX",
            "description": "컨텍스트 메뉴로 빠르게 편집 작업을 수행할 수 있습니다",
            "userValue": "마우스 우클릭으로 빠르게 작업할 수 있어 효율적입니다",
            "technicalNotes": "컨텍스트 메뉴, 제스처"
        }
    },

    "life-restaurant": {
        "방문 횟수": {
            "category": "데이터",
            "description": "각 식당을 몇 번 방문했는지 자동으로 카운트합니다",
            "userValue": "자주 가는 단골 맛집을 쉽게 파악할 수 있습니다",
            "technicalNotes": "카운터, 방문 기록"
        },
        "진짜 맛 있다는 것은": {
            "category": "핵심기능",
            "description": "별점 외에 '진짜 맛있음' 마크를 별도로 표시할 수 있습니다",
            "userValue": "단순 평점을 넘어 정말 추천하고 싶은 곳을 강조할 수 있습니다",
            "technicalNotes": "북마크 플래그, 필터링"
        },
        "검색은 카카오 API": {
            "category": "통합",
            "description": "카카오맵 API로 식당을 검색하고 정보를 가져올 수 있습니다",
            "userValue": "식당 이름만 입력하면 주소와 정보가 자동으로 채워집니다",
            "technicalNotes": "Kakao Local API, 자동완성"
        },
        "특정 위치에 들어가면 알림을 주는 것": {
            "category": "핵심기능",
            "description": "저장한 맛집 근처에 가면 자동으로 알림을 받습니다",
            "userValue": "근처에 왔을 때 방문 예정이던 맛집을 떠올릴 수 있습니다",
            "technicalNotes": "지오펜싱, 위치 기반 알림"
        }
    },

    "rainbow-of-desire": {
        "캘린더를 불러오는 실험": {
            "category": "통합",
            "description": "기기 캘린더와 연동하여 일정과 감정을 함께 볼 수 있습니다",
            "userValue": "어떤 일정이 어떤 감정을 유발했는지 연결하여 이해할 수 있습니다",
            "technicalNotes": "EventKit, 캘린더 권한"
        },
        "일정 패턴 다양하게 시각화 필요": {
            "category": "데이터",
            "description": "감정 데이터를 다양한 차트와 그래프로 표현합니다",
            "userValue": "여러 각도에서 감정 패턴을 분석하고 인사이트를 얻을 수 있습니다",
            "technicalNotes": "차트 라이브러리, 다양한 시각화 옵션"
        },
        "매일 계속되는 것, 시작점과 끝점이 없는것 만들기": {
            "category": "핵심기능",
            "description": "지속적인 감정 상태를 구간 없이 기록할 수 있습니다",
            "userValue": "단발적 감정이 아닌 지속되는 기분을 표현할 수 있습니다",
            "technicalNotes": "연속 기록, 상태 트래킹"
        }
    },

    "rapport-map": {
        "멘티들과 했던 행동들에 사진으로 기억할 수 있도록 돕기": {
            "category": "핵심기능",
            "description": "만남에 사진을 첨부하여 시각적으로 기억할 수 있습니다",
            "userValue": "텍스트만으로는 표현하기 어려운 순간들을 사진으로 생생하게 남길 수 있습니다",
            "technicalNotes": "사진 첨부, 갤러리 통합"
        },
        "기록에 태그를 남기고 태그로 필터링 해서 볼 수 있도록 하기": {
            "category": "데이터",
            "description": "만남이나 대화에 태그를 달아 분류하고 검색할 수 있습니다",
            "userValue": "특정 주제의 대화나 활동을 빠르게 찾아볼 수 있습니다",
            "technicalNotes": "태그 시스템, 다중 필터"
        },
        "위젯으로 다가오는 이벤트 볼 수 있게 해주기": {
            "category": "핵심기능",
            "description": "홈 화면 위젯에서 다가오는 만남 일정을 확인할 수 있습니다",
            "userValue": "앱을 열지 않고도 오늘의 만남 일정을 바로 확인할 수 있습니다",
            "technicalNotes": "WidgetKit, 일정 필터링"
        },
        "녹음 중 일때 좀 더 쉽게 다이나믹 아일랜드": {
            "category": "UI/UX",
            "description": "대화 녹음 중일 때 다이나믹 아일랜드에 상태를 표시합니다",
            "userValue": "녹음 중임을 잊지 않고 쉽게 제어할 수 있습니다",
            "technicalNotes": "Live Activity, 다이나믹 아일랜드 API"
        },
        "Core Spotlight - Spotlight 검색 으로 사람 쉽게 검색하기": {
            "category": "통합",
            "description": "iOS 스포트라이트 검색에서 라포맵의 사람을 찾을 수 있습니다",
            "userValue": "앱을 열지 않고 시스템 검색으로 바로 사람을 찾을 수 있습니다",
            "technicalNotes": "CoreSpotlight, 검색 인덱싱"
        },
        "만난 장소도 기록해주기": {
            "category": "핵심기능",
            "description": "만남이 이루어진 장소를 위치 정보와 함께 저장할 수 있습니다",
            "userValue": "어디서 만났는지 기억하며 장소와 연결된 추억을 떠올릴 수 있습니다",
            "technicalNotes": "위치 권한, 지오코딩"
        },
        "메모에서 자연스럽게 데이터를 추출해서 필요한 곳에 녹이기": {
            "category": "핵심기능",
            "description": "자유로운 메모에서 날짜, 장소 등을 자동으로 인식하여 구조화합니다",
            "userValue": "정해진 양식 없이 자연스럽게 메모만 해도 정보가 정리됩니다",
            "technicalNotes": "NLP, 데이터 파싱"
        },
        "Push Notifications + Background Tasks - 스마트 알림": {
            "category": "핵심기능",
            "description": "오랜만에 연락하지 않은 사람을 알림으로 상기시킵니다",
            "userValue": "소중한 사람과의 연락을 놓치지 않고 관계를 유지할 수 있습니다",
            "technicalNotes": "백그라운드 작업, 푸시 알림"
        },
        "App Intents + Siri Shortcuts - 음성 명령": {
            "category": "통합",
            "description": "시리로 음성 명령하여 빠르게 만남을 기록할 수 있습니다",
            "userValue": "손을 쓰지 않고도 음성으로 만남을 기록할 수 있습니다",
            "technicalNotes": "App Intents, Siri Shortcuts"
        },
        "음성 개선": {
            "category": "핵심기능",
            "description": "대화 녹음 품질과 재생 기능을 개선합니다",
            "userValue": "더 선명한 음질로 대화를 녹음하고 나중에 다시 들을 수 있습니다",
            "technicalNotes": "오디오 녹음, 노이즈 캔슬링"
        },
        "멘토링 트래킹": {
            "category": "데이터",
            "description": "멘토링 세션의 횟수, 주제, 진행 상황을 추적합니다",
            "userValue": "멘티의 성장 과정을 체계적으로 관리하고 피드백할 수 있습니다",
            "technicalNotes": "세션 카운팅, 진행률 시각화"
        },
        "사람관계보기": {
            "category": "데이터",
            "description": "사람들 간의 연결 관계를 시각화하여 보여줍니다",
            "userValue": "네트워크가 어떻게 연결되어 있는지 한눈에 파악할 수 있습니다",
            "technicalNotes": "그래프 시각화, 관계 매핑"
        }
    },

    "schedule-assistant": {
        "너 이거 다 했어? 라고 물어봐주기": {
            "category": "핵심기능",
            "description": "완료하지 않은 작업에 대해 친근하게 알림을 보냅니다",
            "userValue": "잊고 있던 작업을 부담스럽지 않게 상기할 수 있습니다",
            "technicalNotes": "작업 상태 체크, 친근한 알림 메시지"
        }
    },

    "three-meals": {
        "설정 바로반응": {
            "category": "UI/UX",
            "description": "설정 변경 시 앱을 재시작하지 않고 즉시 반영됩니다",
            "userValue": "설정을 바꾸고 바로 결과를 확인할 수 있어 편리합니다",
            "technicalNotes": "Combine, 반응형 UI"
        },
        "이미 가지고 있는 추출한 재료로 줄 수 있는 정보": {
            "category": "데이터",
            "description": "식단에서 추출한 재료 정보를 바탕으로 영양 인사이트를 제공합니다",
            "userValue": "내가 먹은 음식의 영양소를 이해하고 건강한 식습관을 만들 수 있습니다",
            "technicalNotes": "영양소 DB, 데이터 분석"
        },
        "유저가 달 성할 수 있는 목표와 앱의 목표 명확하게 하기": {
            "category": "UI/UX",
            "description": "사용자가 세운 목표와 앱의 가이드를 명확히 구분하여 표시합니다",
            "userValue": "내 목표가 무엇인지 혼란 없이 집중할 수 있습니다",
            "technicalNotes": "목표 UI 개선, 시각적 구분"
        },
        "추출한 식단을 바탕으로 이런거 먹으면 좋아 추천하기": {
            "category": "핵심기능",
            "description": "부족한 영양소를 고려하여 음식을 추천합니다",
            "userValue": "균형 잡힌 식단을 위해 무엇을 먹어야 할지 제안받을 수 있습니다",
            "technicalNotes": "추천 알고리즘, 영양소 균형 계산"
        },
        "사실은 오해하고있을 식단에 대한 정보와 팁": {
            "category": "데이터",
            "description": "잘못된 식단 상식을 바로잡는 정보를 제공합니다",
            "userValue": "건강한 식습관에 대한 올바른 지식을 얻을 수 있습니다",
            "technicalNotes": "콘텐츠 DB, 팁 시스템"
        },
        "사용자의 식단분석 보이기 감추기 토글 설정 + 이미지 작아지지 않게하기": {
            "category": "커스터마이징",
            "description": "식단 분석 정보를 선택적으로 표시하거나 숨길 수 있습니다",
            "userValue": "원하는 정보만 보며 화면을 깔끔하게 유지할 수 있습니다",
            "technicalNotes": "토글 UI, 레이아웃 조정"
        },
        "간식 감추는 설정": {
            "category": "커스터마이징",
            "description": "간식 기록을 메인 화면에서 숨길 수 있습니다",
            "userValue": "식사 기록에만 집중하고 싶을 때 간식을 따로 관리할 수 있습니다",
            "technicalNotes": "필터 설정, 데이터 필터링"
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
    backup_file = app_file.with_suffix('.json.backup3')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original)

    # 저장
    with open(app_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_features_to_app(app_file):
    """앱에 feature 정보 추가"""
    app_id = app_file.stem
    data = load_app_json(app_file)

    if app_id not in TASK_FEATURES:
        return 0

    features_map = TASK_FEATURES[app_id]
    updated_count = 0

    for task in data.get('allTasks', []):
        task_name = task['name']

        # 이미 featureMetadata가 있으면 스킵
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

    if updated_count > 0:
        save_app_json(app_file, data)
        print(f"✅ {data.get('name', app_id)}: {updated_count}개 feature 추가")
        return updated_count
    else:
        return 0


def main():
    """메인 실행"""
    print("=" * 80)
    print("모든 앱에 Feature 정보 추가")
    print("=" * 80)
    print()

    app_files = sorted(APPS_DIR.glob("*.json"))
    total_updated = 0

    for app_file in app_files:
        count = add_features_to_app(app_file)
        total_updated += count

    print()
    print("=" * 80)
    print(f"총 {total_updated}개 feature 추가 완료")
    print("=" * 80)


if __name__ == "__main__":
    main()

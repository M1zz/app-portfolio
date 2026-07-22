#!/usr/bin/env python3
"""
피처 설명 개선 스크립트
각 앱의 특성에 맞게 피처 설명을 개선합니다.
"""

import json
from pathlib import Path
from typing import Dict, List

# 앱별 맞춤형 피처 설명 (사용자 관점: "이 앱은 뭐하는 앱이야?")
APP_FEATURE_IMPROVEMENTS = {
    # 꿈을 찾아서 (Bucket Climb) - 버킷리스트 관리 앱
    "bucket-climb": {
        "사진 첨부 기능 (단일)": {
            "description": "각 버킷리스트 항목에 사진을 추가하여 시각적으로 목표를 구체화할 수 있습니다",
            "userValue": "꿈을 사진으로 기록하고 완료 시 추억을 남길 수 있습니다",
            "technicalNotes": "PhotoKit을 사용한 갤러리 접근 및 이미지 첨부"
        },
        "다중 사진 첨부 기능 구현": {
            "description": "하나의 버킷리스트에 여러 장의 사진을 추가하여 과정을 기록할 수 있습니다",
            "userValue": "목표 달성 과정을 여러 사진으로 기록하고 스토리로 만들 수 있습니다",
            "technicalNotes": "PHPickerViewController를 사용한 다중 선택 지원"
        },
        "소셜 공유 기능": {
            "description": "완료한 버킷리스트를 SNS에 공유하여 친구들과 성취를 나눌 수 있습니다",
            "userValue": "성취한 목표를 친구들과 공유하며 동기부여를 얻을 수 있습니다",
            "technicalNotes": "UIActivityViewController를 통한 공유 시트 구현"
        }
    },

    # 클립키보드 - 텍스트 템플릿 키보드 앱
    "clip-keyboard": {
        "템플릿 기능 추가": {
            "description": "자주 사용하는 텍스트를 템플릿으로 저장하고 커스텀 키보드에서 빠르게 입력할 수 있습니다",
            "userValue": "매번 반복해서 타이핑하는 이메일, 주소, 인사말 등을 한 번의 탭으로 입력하여 시간을 절약합니다",
            "technicalNotes": "CoreData로 템플릿 저장, Custom Keyboard Extension 구현"
        },
        "아이 클라우드로 메모 동기화": {
            "description": "저장한 템플릿을 iCloud를 통해 모든 Apple 기기에서 자동으로 동기화합니다",
            "userValue": "iPhone, iPad, Mac 어디서든 동일한 템플릿을 사용할 수 있어 기기 간 전환이 자유롭습니다",
            "technicalNotes": "CloudKit 프레임워크 사용, 충돌 해결 로직 구현"
        },
        "백업 복원 하는 기능": {
            "description": "템플릿 데이터를 백업하고 필요할 때 복원할 수 있습니다",
            "userValue": "기기 변경이나 앱 재설치 시에도 템플릿을 잃어버리지 않고 안전하게 보관합니다",
            "technicalNotes": "JSON 기반 백업 파일 생성 및 복원 기능"
        },
        "faceID로 보안": {
            "description": "Face ID 또는 Touch ID로 민감한 템플릿을 잠금 설정하여 보호할 수 있습니다",
            "userValue": "비밀번호, 계좌번호 등 민감한 정보를 템플릿으로 저장해도 안전합니다",
            "technicalNotes": "LocalAuthentication 프레임워크를 사용한 생체 인증"
        },
        "카테고리 관리": {
            "description": "템플릿을 카테고리별로 분류하여 체계적으로 정리할 수 있습니다",
            "userValue": "업무용, 개인용 등으로 나누어 필요한 템플릿을 빠르게 찾을 수 있습니다",
            "technicalNotes": "계층적 카테고리 구조, 드래그 앤 드롭 재정렬"
        },
        "키보드 레이아웃 열 개수 설정 기능": {
            "description": "키보드의 버튼 배열을 2열, 3열, 4열 등으로 자유롭게 조정할 수 있습니다",
            "userValue": "화면 크기와 손가락 크기에 맞게 키보드를 최적화하여 더 편하게 사용합니다",
            "technicalNotes": "UICollectionView 레이아웃 동적 조정, UserDefaults 저장"
        },
        "버튼 높이/글자 크기 슬라이더 조정 기능": {
            "description": "키보드 버튼의 크기와 글자 크기를 슬라이더로 세밀하게 조정할 수 있습니다",
            "userValue": "시력이 안 좋거나 손가락이 큰 경우에도 편안하게 사용할 수 있도록 개인화합니다",
            "technicalNotes": "동적 타이포그래피, 접근성 지원, Dynamic Type"
        }
    },

    # 라포 맵 - 인간관계 관리 앱
    "rapport-map": {
        "데이터를 마구 던지면 저장해주는 메모 기능": {
            "description": "만난 사람과의 대화 내용을 빠르게 메모로 남길 수 있습니다",
            "userValue": "중요한 대화나 약속을 잊지 않고 나중에 다시 확인할 수 있습니다",
            "technicalNotes": "텍스트 입력 자동 저장, 실시간 동기화"
        },
        "멘토링이나 어떤 특정 태그처럼 속성 중에 멘토링 케이스를 추가할 수 있었으면 좋겠음": {
            "description": "인간관계를 멘토링, 친구, 동료 등의 유형으로 분류할 수 있습니다",
            "userValue": "각 관계의 특성에 맞게 관리하고 필요한 정보를 효율적으로 찾을 수 있습니다",
            "technicalNotes": "태그 시스템, 필터링 및 검색 기능"
        },
        "클라우드 동기화": {
            "description": "인간관계 데이터를 iCloud로 자동 동기화합니다",
            "userValue": "여러 기기에서 동일한 관계 정보를 확인하고 업데이트할 수 있습니다",
            "technicalNotes": "CloudKit 기반 실시간 동기화"
        },
        "MessageUI - 빠른 연락": {
            "description": "앱에서 바로 메시지나 전화를 걸 수 있습니다",
            "userValue": "연락처를 따로 찾지 않고 바로 소통할 수 있어 편리합니다",
            "technicalNotes": "MessageUI 프레임워크, CallKit 통합"
        },
        "클라우드 백업기능": {
            "description": "중요한 인간관계 데이터를 클라우드에 백업합니다",
            "userValue": "기기를 잃어버려도 관계 정보를 안전하게 복원할 수 있습니다",
            "technicalNotes": "자동 백업 스케줄링, 암호화 저장"
        }
    },

    # 세끼 - 식단 기록 및 분석 앱
    "three-meals": {
        "식단 피드백 작성기능 추가": {
            "description": "먹은 음식에 대한 느낌이나 메모를 남길 수 있습니다",
            "userValue": "식사 후 느낀 점을 기록하여 건강한 식습관을 만들어갈 수 있습니다",
            "technicalNotes": "텍스트 에디터, 감정 태그 기능"
        },
        "좀 더 나은 운동 디자인으로 바꾸기": {
            "description": "운동 기록 화면을 더 보기 좋고 사용하기 편하게 개선합니다",
            "userValue": "직관적인 인터페이스로 운동 기록을 즐겁게 할 수 있습니다",
            "technicalNotes": "SwiftUI 리디자인, 애니메이션 개선"
        }
    },

    # 바미로그 - 출산/육아 기록 앱
    "bami-log": {
        "진통기록 + 호흡을 도와주는 것 추가": {
            "description": "진통 시간을 기록하고 호흡법을 안내받을 수 있습니다",
            "userValue": "출산 과정에서 진통 간격을 정확히 측정하고 호흡을 조절하는데 도움을 받습니다",
            "technicalNotes": "타이머 기능, 호흡 가이드 애니메이션"
        }
    },

    # 돈꼬마트 - 장보기 리스트 앱
    "donkko-mart": {
        "나의 마트 추가하는 경험 개선": {
            "description": "자주 가는 마트를 쉽게 등록하고 관리할 수 있습니다",
            "userValue": "마트별로 장보기 목록을 따로 관리하여 더 효율적으로 쇼핑합니다",
            "technicalNotes": "위치 기반 마트 제안, 즐겨찾기 기능"
        },
        "위젯 화면 개선": {
            "description": "홈 화면 위젯에서 장보기 목록을 한눈에 확인할 수 있습니다",
            "userValue": "앱을 열지 않고도 필요한 물건을 빠르게 확인할 수 있습니다",
            "technicalNotes": "WidgetKit, 다양한 위젯 크기 지원"
        },
        "개발자 소통화면": {
            "description": "앱 개발자에게 피드백이나 제안을 전달할 수 있는 화면입니다",
            "userValue": "원하는 기능을 제안하거나 문제를 빠르게 신고할 수 있습니다",
            "technicalNotes": "이메일 통합, 피드백 폼"
        }
    },

    # 두 번 알림 - 알림 관리 앱
    "double-reminder": {
        "UI 개선작업": {
            "description": "알림 관리 화면을 더 직관적이고 사용하기 편하게 개선합니다",
            "userValue": "복잡한 알림도 쉽게 설정하고 관리할 수 있습니다",
            "technicalNotes": "SwiftUI 기반 리디자인"
        },
        "내가 기록한 정보 중 저장된 것 아이클라우드 동기화": {
            "description": "설정한 알림을 iCloud로 자동 동기화합니다",
            "userValue": "여러 기기에서 동일한 알림을 받을 수 있습니다",
            "technicalNotes": "CloudKit 기반 동기화"
        }
    },

    # 인생 맛집 - 맛집 기록 앱
    "life-restaurant": {
        "사람들 추가하기": {
            "description": "함께 간 사람을 맛집 기록에 추가할 수 있습니다",
            "userValue": "누구와 어떤 맛집을 갔는지 기억할 수 있어 추억을 더 풍부하게 남깁니다",
            "technicalNotes": "연락처 통합, 태그 시스템"
        },
        "친구에게 리스트 공유할 수 있게하기": {
            "description": "내 맛집 리스트를 친구들과 공유할 수 있습니다",
            "userValue": "맛집 추천을 쉽게 공유하고 함께 방문 계획을 세울 수 있습니다",
            "technicalNotes": "딥링크, 공유 시트 구현"
        }
    },

    # 오늘의 주접 - 칭찬 앱
    "daily-compliment": {
        "컨텐츠 추가": {
            "description": "다양한 칭찬 메시지와 주접 멘트를 추가합니다",
            "userValue": "매일 새로운 칭찬을 받으며 긍정적인 하루를 시작할 수 있습니다",
            "technicalNotes": "콘텐츠 DB 관리, 랜덤 선택 알고리즘"
        }
    },

    # 퀴즈 - 퀴즈 앱
    "quiz": {
        "캐싱으로 문제 저장 및 API 최소화": {
            "description": "한번 받은 퀴즈 문제를 저장하여 오프라인에서도 풀 수 있습니다",
            "userValue": "인터넷 없이도 퀴즈를 즐길 수 있고 로딩 시간이 줄어듭니다",
            "technicalNotes": "CoreData 캐싱, 네트워크 요청 최적화"
        }
    },

    # 욕망의 무지개 - 습관 추적 앱
    "rainbow-of-desire": {
        "특정 날짜만 제외하는 기능": {
            "description": "휴가나 특별한 날을 습관 추적에서 제외할 수 있습니다",
            "userValue": "유연하게 습관을 관리하여 완벽주의에 빠지지 않고 지속할 수 있습니다",
            "technicalNotes": "날짜 예외 처리, 캘린더 통합"
        },
        "클라우드 킷 적용해서 데이터 동기화": {
            "description": "습관 기록을 iCloud로 자동 동기화합니다",
            "userValue": "기기를 바꿔도 습관 기록이 유지되어 꾸준히 추적할 수 있습니다",
            "technicalNotes": "CloudKit 프레임워크"
        },
        "일정관리 리스트로 하기": {
            "description": "습관을 일정처럼 관리할 수 있습니다",
            "userValue": "체계적으로 습관을 계획하고 실천할 수 있습니다",
            "technicalNotes": "리스트 뷰, 정렬 및 필터링"
        }
    }
}


def improve_features():
    """피처 설명 개선"""
    apps_dir = Path(__file__).parent.parent / 'projects/PortfolioCEO/PortfolioCEO/Data/apps'

    print("📝 피처 설명 개선 시작...")
    print("=" * 60)

    improved_count = 0

    for app_id, improvements in APP_FEATURE_IMPROVEMENTS.items():
        json_file = apps_dir / f"{app_id}.json"

        if not json_file.exists():
            print(f"⚠️  {app_id}.json 파일을 찾을 수 없습니다")
            continue

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        app_name = data.get('name', app_id)
        print(f"\n📱 {app_name}")

        updated = False
        for task in data.get('allTasks', []):
            task_name = task.get('name', '')

            if task_name in improvements:
                # 기존 메타데이터 가져오기 (없으면 생성)
                if 'featureMetadata' not in task:
                    task['featureMetadata'] = {}

                if 'labels' not in task or 'feature' not in task['labels']:
                    if 'labels' not in task:
                        task['labels'] = []
                    task['labels'].append('feature')

                # 개선된 내용으로 업데이트
                improvement = improvements[task_name]
                task['featureMetadata']['description'] = improvement['description']
                task['featureMetadata']['userValue'] = improvement['userValue']

                if improvement.get('technicalNotes'):
                    task['featureMetadata']['technicalNotes'] = improvement['technicalNotes']

                print(f"  ✓ {task_name}")
                improved_count += 1
                updated = True

        # 파일 저장
        if updated:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  💾 저장 완료")

    print("\n" + "=" * 60)
    print(f"✨ 총 {improved_count}개 피처 설명 개선 완료!")


if __name__ == '__main__':
    improve_features()

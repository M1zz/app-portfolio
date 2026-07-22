#!/usr/bin/env python3
"""
vision.md와 feature.md를 바탕으로 각 앱의 비전과 기능 정보를 수집하는 스크립트
"""

import json
import os
from pathlib import Path
from datetime import datetime

# 경로 설정
APPS_DIR = Path("/Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO/Data/apps")

# 앱별 비전 및 기능 정보 (기존 데이터와 추가 분석)
APP_VISIONS = {
    "bami-log": {
        "vision": {
            "tagline": "개발자의 학습 동반자",
            "coreValue": "학습한 내용을 체계적으로 기록하고 복습하여 장기 기억으로 전환",
            "targetUsers": "꾸준히 공부하는 개발자, 학생, 평생 학습자",
            "uniqueSellingPoint": "단순 노트가 아닌 복습 주기 기반 학습 관리 시스템",
            "designPrinciples": [
                "빠른 기록 - 배운 것을 바로 메모",
                "주기적 복습 - 망각 곡선 기반 알림",
                "진행 추적 - 학습량 시각화"
            ],
            "userExperienceGoals": [
                "학습 직후 30초 안에 기록",
                "복습 알림으로 장기 기억 형성",
                "학습 진행도 한눈에 파악"
            ]
        },
        "features": [
            {
                "name": "학습 노트 작성",
                "category": "핵심기능",
                "description": "배운 내용을 빠르게 기록하고 태그로 분류할 수 있습니다",
                "userValue": "수업이나 독서 직후 핵심 내용을 놓치지 않고 정리할 수 있습니다",
                "technicalNotes": "마크다운 에디터, 태그 시스템"
            },
            {
                "name": "복습 스케줄링",
                "category": "핵심기능",
                "description": "망각 곡선 기반으로 복습 시기를 자동 알림합니다",
                "userValue": "언제 복습해야 할지 고민하지 않고 알림을 따라 효율적으로 학습합니다",
                "technicalNotes": "간격 반복 알고리즘, 로컬 알림"
            }
        ]
    },

    "cooltime": {
        "vision": {
            "tagline": "눈 건강 지키미",
            "coreValue": "장시간 화면 사용으로부터 눈을 보호하는 휴식 관리",
            "targetUsers": "장시간 컴퓨터를 사용하는 개발자, 디자이너, 직장인",
            "uniqueSellingPoint": "20-20-20 규칙(20분마다 20초간 20피트 먼 곳 보기)을 자동으로 관리",
            "designPrinciples": [
                "자동 알림 - 사용자가 잊지 않도록",
                "방해 최소화 - 중요한 작업 중단 방지",
                "습관 형성 - 꾸준한 휴식 패턴 만들기"
            ],
            "userExperienceGoals": [
                "20분마다 부드러운 알림",
                "휴식 중 눈 운동 가이드",
                "하루 휴식 횟수 추적"
            ]
        },
        "features": [
            {
                "name": "자동 타이머",
                "category": "핵심기능",
                "description": "20분마다 자동으로 휴식 시간을 알려줍니다",
                "userValue": "타이머를 직접 설정하지 않아도 규칙적으로 눈을 쉴 수 있습니다",
                "technicalNotes": "백그라운드 타이머, 알림 권한"
            },
            {
                "name": "눈 운동 가이드",
                "category": "UI/UX",
                "description": "휴식 시간에 따라할 수 있는 간단한 눈 운동을 제공합니다",
                "userValue": "단순히 쉬는 것이 아니라 눈 건강에 도움이 되는 운동을 할 수 있습니다",
                "technicalNotes": "애니메이션 가이드, 타이머"
            }
        ]
    },

    "daily-compliment": {
        "vision": {
            "tagline": "매일의 긍정 에너지",
            "coreValue": "하루를 시작하는 따뜻한 칭찬으로 자존감과 동기부여",
            "targetUsers": "긍정적인 하루를 원하는 모든 사람, 특히 자존감이 낮거나 동기부여가 필요한 사람",
            "uniqueSellingPoint": "매일 아침 개인 맞춤형 칭찬 메시지로 하루를 시작",
            "designPrinciples": [
                "따뜻함 - 진심이 느껴지는 메시지",
                "다양성 - 매일 다른 칭찬",
                "개인화 - 사용자 맥락 반영"
            ],
            "userExperienceGoals": [
                "아침에 첫 화면으로 칭찬 받기",
                "기분 좋게 하루 시작",
                "누적된 칭찬으로 자존감 향상"
            ]
        },
        "features": [
            {
                "name": "일일 칭찬 메시지",
                "category": "핵심기능",
                "description": "매일 아침 새로운 칭찬 메시지를 받을 수 있습니다",
                "userValue": "긍정적인 에너지로 하루를 시작할 수 있습니다",
                "technicalNotes": "로컬 알림, 메시지 DB"
            },
            {
                "name": "칭찬 모음집",
                "category": "데이터",
                "description": "받았던 칭찬들을 모아서 다시 볼 수 있습니다",
                "userValue": "힘든 날 과거의 칭찬을 다시 보며 위로받을 수 있습니다",
                "technicalNotes": "Core Data 저장, 날짜별 분류"
            }
        ]
    },

    "double-reminder": {
        "vision": {
            "tagline": "잊지 않는 두 번의 기회",
            "coreValue": "중요한 일을 두 번 알려줘서 절대 놓치지 않게",
            "targetUsers": "건망증이 있거나 중요한 일정을 자주 놓치는 사람",
            "uniqueSellingPoint": "한 번이 아닌 두 번 알림으로 확실하게 상기",
            "designPrinciples": [
                "이중 안전망 - 한 번 놓쳐도 괜찮아",
                "유연한 간격 - 상황에 맞는 알림 간격",
                "맥락 인식 - 적절한 타이밍에 알림"
            ],
            "userExperienceGoals": [
                "중요한 일정 절대 놓치지 않기",
                "두 번째 알림으로 안심",
                "알림 간격 자유롭게 설정"
            ]
        },
        "features": [
            {
                "name": "이중 알림 설정",
                "category": "핵심기능",
                "description": "하나의 일정에 두 번의 알림을 설정할 수 있습니다",
                "userValue": "첫 번째 알림을 놓쳐도 두 번째 알림으로 확인할 수 있습니다",
                "technicalNotes": "다중 로컬 알림, 스누즈 기능"
            },
            {
                "name": "유연한 간격 설정",
                "category": "커스터마이징",
                "description": "첫 번째와 두 번째 알림 사이의 간격을 자유롭게 조정할 수 있습니다",
                "userValue": "상황에 맞게 5분 전, 1시간 전 등 원하는 간격으로 알림을 받을 수 있습니다",
                "technicalNotes": "커스텀 타이머, 시간 선택 UI"
            }
        ]
    },

    "ecdesigner": {
        "vision": {
            "tagline": "모두를 위한 명함 디자이너",
            "coreValue": "디자인 지식 없이도 전문적인 명함을 만들 수 있는 경험",
            "targetUsers": "프리랜서, 소상공인, 개인 사업자",
            "uniqueSellingPoint": "템플릿 기반으로 5분 안에 명함 디자인 완성",
            "designPrinciples": [
                "템플릿 중심 - 빈 캔버스의 부담 없이",
                "직관적 편집 - 드래그 앤 드롭으로 간단하게",
                "즉시 미리보기 - 실제 인쇄 모습 확인"
            ],
            "userExperienceGoals": [
                "5분 안에 명함 디자인 완성",
                "전문적인 결과물",
                "즉시 인쇄 가능한 파일 생성"
            ]
        },
        "features": [
            {
                "name": "명함 템플릿",
                "category": "핵심기능",
                "description": "다양한 직업과 스타일의 명함 템플릿을 제공합니다",
                "userValue": "디자인을 처음부터 할 필요 없이 마음에 드는 템플릿을 골라 시작할 수 있습니다",
                "technicalNotes": "템플릿 라이브러리, 카테고리 필터링"
            },
            {
                "name": "드래그 앤 드롭 편집",
                "category": "UI/UX",
                "description": "텍스트, 로고, 아이콘을 드래그로 자유롭게 배치할 수 있습니다",
                "userValue": "복잡한 도구 없이 직관적으로 명함을 커스터마이징할 수 있습니다",
                "technicalNotes": "제스처 인식, 레이어 관리"
            }
        ]
    },

    "life-restaurant": {
        "vision": {
            "tagline": "맛집 기록의 새로운 기준",
            "coreValue": "먹었던 맛집을 기록하고 공유하여 더 나은 외식 경험",
            "targetUsers": "외식을 즐기고 맛집 탐방을 좋아하는 사람들",
            "uniqueSellingPoint": "사진, 메모, 평점을 한곳에 모아 나만의 맛집 지도 생성",
            "designPrinciples": [
                "사진 중심 - 음식은 보는 것부터",
                "위치 기반 - 지도에서 한눈에",
                "개인 평가 - 대중 평점이 아닌 내 기준"
            ],
            "userExperienceGoals": [
                "식사 후 30초 안에 기록",
                "지도에서 주변 내 맛집 확인",
                "친구에게 추천 공유"
            ]
        },
        "features": [
            {
                "name": "맛집 기록",
                "category": "핵심기능",
                "description": "방문한 식당의 사진, 메뉴, 평점, 메모를 저장할 수 있습니다",
                "userValue": "나중에 다시 방문하거나 추천할 때 정확한 정보를 기억할 수 있습니다",
                "technicalNotes": "사진 첨부, 평점 UI, 메모 에디터"
            },
            {
                "name": "맛집 지도",
                "category": "핵심기능",
                "description": "기록한 맛집들을 지도에 표시하여 한눈에 볼 수 있습니다",
                "userValue": "현재 위치 근처의 내가 가본 맛집을 빠르게 찾을 수 있습니다",
                "technicalNotes": "MapKit, 위치 권한, 커스텀 핀"
            }
        ]
    },

    "pixel-mimi": {
        "vision": {
            "tagline": "픽셀 아트의 즐거움",
            "coreValue": "누구나 쉽게 픽셀 아트를 그리고 공유하는 경험",
            "targetUsers": "픽셀 아트를 좋아하는 사람, 간단한 그림을 그리고 싶은 사람",
            "uniqueSellingPoint": "모바일에 최적화된 픽셀 아트 에디터",
            "designPrinciples": [
                "단순함 - 복잡한 도구 없이",
                "즉각적 피드백 - 그리는 즉시 확인",
                "공유 중심 - SNS로 바로 공유"
            ],
            "userExperienceGoals": [
                "5분 안에 작은 픽셀 아트 완성",
                "직관적인 그리기 도구",
                "완성작 즉시 공유"
            ]
        },
        "features": [
            {
                "name": "픽셀 캔버스",
                "category": "핵심기능",
                "description": "다양한 크기의 픽셀 그리드에서 그림을 그릴 수 있습니다",
                "userValue": "종이에 그리듯 자유롭게 픽셀 아트를 만들 수 있습니다",
                "technicalNotes": "그리드 뷰, 터치 제스처"
            },
            {
                "name": "색상 팔레트",
                "category": "UI/UX",
                "description": "다양한 색상을 쉽게 선택하고 저장할 수 있습니다",
                "userValue": "자주 쓰는 색을 저장해서 일관된 스타일로 그릴 수 있습니다",
                "technicalNotes": "컬러 피커, 팔레트 저장"
            }
        ]
    },

    "probability-calculator": {
        "vision": {
            "tagline": "확률의 직관적 이해",
            "coreValue": "복잡한 확률 계산을 시각화하여 쉽게 이해",
            "targetUsers": "확률을 계산해야 하는 학생, 게이머, 의사결정자",
            "uniqueSellingPoint": "수식이 아닌 시각적 표현으로 확률 계산",
            "designPrinciples": [
                "시각화 우선 - 숫자보다 그래프로",
                "단계별 계산 - 과정을 보여주기",
                "실전 예제 - 실생활 문제 적용"
            ],
            "userExperienceGoals": [
                "확률 문제 입력 후 즉시 결과",
                "시각적으로 이해하기 쉬운 표현",
                "계산 과정 학습"
            ]
        },
        "features": [
            {
                "name": "확률 계산기",
                "category": "핵심기능",
                "description": "조합, 순열, 조건부 확률 등을 계산할 수 있습니다",
                "userValue": "복잡한 수식을 외우지 않아도 확률을 계산할 수 있습니다",
                "technicalNotes": "확률 알고리즘, 입력 검증"
            },
            {
                "name": "시각화 그래프",
                "category": "UI/UX",
                "description": "계산 결과를 차트와 그래프로 표현합니다",
                "userValue": "숫자만으로는 이해하기 어려운 확률을 직관적으로 파악할 수 있습니다",
                "technicalNotes": "차트 라이브러리, 애니메이션"
            }
        ]
    },

    "quiz": {
        "vision": {
            "tagline": "지식을 게임처럼",
            "coreValue": "퀴즈를 통한 재미있는 학습과 지식 테스트",
            "targetUsers": "새로운 것을 배우고 싶은 사람, 지식을 테스트하고 싶은 사람",
            "uniqueSellingPoint": "다양한 주제의 퀴즈를 직접 만들고 공유",
            "designPrinciples": [
                "게이미피케이션 - 점수, 레벨, 배지",
                "다양성 - 여러 주제와 난이도",
                "커뮤니티 - 사용자 생성 콘텐츠"
            ],
            "userExperienceGoals": [
                "퀴즈 풀며 재미있게 학습",
                "나만의 퀴즈 쉽게 만들기",
                "친구와 점수 경쟁"
            ]
        },
        "features": [
            {
                "name": "퀴즈 플레이",
                "category": "핵심기능",
                "description": "다양한 주제의 퀴즈를 풀고 점수를 획득할 수 있습니다",
                "userValue": "재미있게 퀴즈를 풀며 새로운 지식을 배울 수 있습니다",
                "technicalNotes": "퀴즈 엔진, 타이머, 점수 계산"
            },
            {
                "name": "퀴즈 생성",
                "category": "핵심기능",
                "description": "나만의 퀴즈를 만들고 다른 사람과 공유할 수 있습니다",
                "userValue": "내가 아는 지식을 퀴즈로 만들어 친구들과 나눌 수 있습니다",
                "technicalNotes": "에디터, 이미지 첨부, 공유 기능"
            }
        ]
    },

    "rainbow-of-desire": {
        "vision": {
            "tagline": "감정의 색깔을 찾아서",
            "coreValue": "복잡한 감정을 색깔로 표현하고 이해하는 감정 일기",
            "targetUsers": "자신의 감정을 탐구하고 싶은 사람, 감정 관리가 필요한 사람",
            "uniqueSellingPoint": "감정을 무지개 색깔로 시각화하여 패턴 파악",
            "designPrinciples": [
                "색상 중심 - 말보다 색으로",
                "비판단적 - 모든 감정은 괜찮아",
                "패턴 발견 - 감정의 흐름 이해"
            ],
            "userExperienceGoals": [
                "하루 감정을 색으로 표현",
                "감정 패턴 시각적으로 파악",
                "감정 변화 추이 확인"
            ]
        },
        "features": [
            {
                "name": "감정 색상 기록",
                "category": "핵심기능",
                "description": "매일의 감정을 색깔로 선택하고 간단한 메모를 남길 수 있습니다",
                "userValue": "복잡한 감정을 쉽게 표현하고 기록할 수 있습니다",
                "technicalNotes": "컬러 선택 UI, 간단한 메모 입력"
            },
            {
                "name": "감정 캘린더",
                "category": "데이터",
                "description": "한 달간의 감정 변화를 색상 캘린더로 한눈에 볼 수 있습니다",
                "userValue": "나의 감정 패턴을 시각적으로 파악하고 이해할 수 있습니다",
                "technicalNotes": "캘린더 뷰, 색상 그리드"
            }
        ]
    },

    "rebound-journal": {
        "vision": {
            "tagline": "회복의 기록",
            "coreValue": "어려운 시기를 극복하는 과정을 기록하고 성장 추적",
            "targetUsers": "힘든 시기를 겪고 있거나 극복 중인 사람",
            "uniqueSellingPoint": "회복 여정을 단계별로 기록하고 긍정적 변화 시각화",
            "designPrinciples": [
                "공감 - 따뜻하고 이해하는 톤",
                "희망 - 긍정적 변화 강조",
                "프라이버시 - 안전한 개인 공간"
            ],
            "userExperienceGoals": [
                "부담 없이 솔직한 기록",
                "작은 진전도 축하",
                "회복 과정 시각적으로 확인"
            ]
        },
        "features": [
            {
                "name": "회복 일지",
                "category": "핵심기능",
                "description": "매일의 감정과 상태를 기록하고 긍정적 변화를 메모할 수 있습니다",
                "userValue": "회복 과정을 기록하며 작은 진전도 놓치지 않고 확인할 수 있습니다",
                "technicalNotes": "일지 에디터, 감정 트래킹"
            },
            {
                "name": "회복 그래프",
                "category": "데이터",
                "description": "시간에 따른 감정 변화를 그래프로 시각화합니다",
                "userValue": "전체적인 회복 추이를 확인하며 희망을 얻을 수 있습니다",
                "technicalNotes": "차트 라이브러리, 데이터 분석"
            }
        ]
    },

    "relax-on": {
        "vision": {
            "tagline": "언제 어디서나 힐링",
            "coreValue": "자연 소리와 명상으로 일상 속 스트레스 해소",
            "targetUsers": "스트레스가 많은 직장인, 수면에 어려움을 겪는 사람",
            "uniqueSellingPoint": "고품질 자연 소리와 가이드 명상을 제공하는 힐링 앱",
            "designPrinciples": [
                "고요함 - 미니멀한 디자인",
                "몰입 - 방해 요소 제거",
                "개인화 - 취향에 맞는 소리 조합"
            ],
            "userExperienceGoals": [
                "10초 안에 원하는 소리 재생",
                "스트레스 해소와 집중력 향상",
                "편안한 수면 유도"
            ]
        },
        "features": [
            {
                "name": "자연 소리 재생",
                "category": "핵심기능",
                "description": "비, 파도, 새소리 등 다양한 자연 소리를 재생할 수 있습니다",
                "userValue": "자연 소리를 들으며 스트레스를 해소하고 집중력을 높일 수 있습니다",
                "technicalNotes": "오디오 플레이어, 백그라운드 재생"
            },
            {
                "name": "소리 믹싱",
                "category": "커스터마이징",
                "description": "여러 자연 소리를 동시에 재생하고 볼륨을 조절할 수 있습니다",
                "userValue": "나만의 완벽한 힐링 사운드를 만들 수 있습니다",
                "technicalNotes": "멀티 트랙 오디오, 볼륨 컨트롤"
            }
        ]
    },

    "schedule-assistant": {
        "vision": {
            "tagline": "AI 일정 비서",
            "coreValue": "똑똑한 일정 관리로 시간 활용 최적화",
            "targetUsers": "바쁜 일정을 관리하는 직장인, 프리랜서",
            "uniqueSellingPoint": "AI 기반 일정 추천과 자동 시간 배분",
            "designPrinciples": [
                "자동화 - AI가 제안하는 최적 일정",
                "유연성 - 쉬운 조정과 변경",
                "통합 - 캘린더 앱과 연동"
            ],
            "userExperienceGoals": [
                "일정 입력만으로 최적 시간 제안",
                "충돌 없는 스케줄 관리",
                "시간 활용 효율 향상"
            ]
        },
        "features": [
            {
                "name": "스마트 일정 추천",
                "category": "핵심기능",
                "description": "일정의 우선순위와 소요 시간을 고려하여 최적의 시간대를 제안합니다",
                "userValue": "언제 무엇을 할지 고민하지 않고 AI의 제안을 따를 수 있습니다",
                "technicalNotes": "일정 최적화 알고리즘, ML 모델"
            },
            {
                "name": "캘린더 통합",
                "category": "통합",
                "description": "기존 캘린더 앱과 연동하여 일정을 동기화합니다",
                "userValue": "여러 캘린더를 한곳에서 관리할 수 있습니다",
                "technicalNotes": "EventKit, 캘린더 API"
            }
        ]
    },

    "shared-day-designer": {
        "vision": {
            "tagline": "함께 만드는 하루",
            "coreValue": "가족이나 팀과 일정을 공유하고 협업하는 플래너",
            "targetUsers": "가족, 커플, 팀 단위로 일정을 공유하는 사람들",
            "uniqueSellingPoint": "실시간 동기화되는 공유 플래너",
            "designPrinciples": [
                "협업 중심 - 여러 사람이 함께",
                "실시간 - 즉시 반영되는 변경사항",
                "명확성 - 누가 무엇을 하는지 한눈에"
            ],
            "userExperienceGoals": [
                "가족 일정 실시간 확인",
                "일정 충돌 사전 방지",
                "함께 계획하는 즐거움"
            ]
        },
        "features": [
            {
                "name": "공유 캘린더",
                "category": "핵심기능",
                "description": "가족이나 팀원과 캘린더를 공유하고 함께 일정을 관리할 수 있습니다",
                "userValue": "서로의 일정을 실시간으로 확인하고 조율할 수 있습니다",
                "technicalNotes": "실시간 동기화, 권한 관리"
            },
            {
                "name": "일정 알림",
                "category": "핵심기능",
                "description": "공유된 일정에 대한 알림을 모든 구성원이 받을 수 있습니다",
                "userValue": "중요한 가족 일정을 놓치지 않을 수 있습니다",
                "technicalNotes": "푸시 알림, 알림 설정"
            }
        ]
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
    backup_file = app_file.with_suffix('.json.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original)

    # 저장
    with open(app_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_app_with_vision_features(app_file):
    """앱에 vision과 feature 정보 추가"""
    app_id = app_file.stem

    # 이미 vision이 있으면 스킵
    data = load_app_json(app_file)
    if 'vision' in data and data['vision']:
        print(f"✓ {data.get('name', app_id)}: 이미 vision 정보가 있습니다")
        return False

    # vision 정보가 있는지 확인
    if app_id not in APP_VISIONS:
        print(f"⚠ {data.get('name', app_id)}: vision 정보가 준비되지 않았습니다")
        return False

    vision_data = APP_VISIONS[app_id]

    # vision 추가
    data['vision'] = vision_data['vision']

    # feature 정보를 allTasks에 추가
    if 'features' in vision_data:
        updated_count = 0
        for feature_info in vision_data['features']:
            # 해당 feature 이름과 일치하는 task 찾기
            for task in data.get('allTasks', []):
                if task['name'] == feature_info['name']:
                    # labels 추가
                    if 'labels' not in task:
                        task['labels'] = []
                    if 'feature' not in task['labels']:
                        task['labels'].append('feature')

                    # featureMetadata 추가
                    task['featureMetadata'] = {
                        'category': feature_info['category'],
                        'description': feature_info['description'],
                        'userValue': feature_info['userValue'],
                        'technicalNotes': feature_info['technicalNotes']
                    }
                    updated_count += 1
                    break
            else:
                # task가 없으면 새로 생성
                new_task = {
                    'name': feature_info['name'],
                    'status': 'not-started',
                    'targetDate': None,
                    'targetVersion': None,
                    'labels': ['feature'],
                    'featureMetadata': {
                        'category': feature_info['category'],
                        'description': feature_info['description'],
                        'userValue': feature_info['userValue'],
                        'technicalNotes': feature_info['technicalNotes']
                    }
                }
                data['allTasks'].append(new_task)
                updated_count += 1

    # 저장
    save_app_json(app_file, data)
    print(f"✅ {data.get('name', app_id)}: vision 추가, {updated_count}개 feature 업데이트")
    return True


def main():
    """메인 실행"""
    print("=" * 60)
    print("Vision & Feature 정보 수집")
    print("=" * 60)
    print()

    app_files = sorted(APPS_DIR.glob("*.json"))

    updated = 0
    skipped = 0
    missing = 0

    for app_file in app_files:
        result = update_app_with_vision_features(app_file)
        if result:
            updated += 1
        elif result is False:
            app_id = app_file.stem
            data = load_app_json(app_file)
            if 'vision' in data and data['vision']:
                skipped += 1
            else:
                missing += 1

    print()
    print("=" * 60)
    print(f"완료: {updated}개 앱 업데이트")
    print(f"스킵: {skipped}개 앱 (이미 vision 있음)")
    print(f"대기: {missing}개 앱 (vision 준비 필요)")
    print("=" * 60)


if __name__ == "__main__":
    main()

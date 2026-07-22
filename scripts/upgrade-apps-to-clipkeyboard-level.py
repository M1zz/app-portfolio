#!/usr/bin/env python3
"""
11개 앱을 클립키보드 수준(10개 이상 feature)으로 업그레이드
20년차 기획자 관점에서 "당연히 있어야 할 기능" 추가
"""

import json
from pathlib import Path
from datetime import datetime

APPS_DIR = Path("/Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO/Data/apps")

# 각 앱별 추가할 feature 목록
NEW_FEATURES = {
    "cooltime": [
        {
            "name": "휴식 통계 대시보드",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "진행 추적",
                "description": "일별, 주별, 월별 휴식 횟수와 패턴을 시각화합니다",
                "userValue": "내가 얼마나 규칙적으로 눈을 쉬고 있는지 확인할 수 있습니다",
                "technicalNotes": "Charts 라이브러리, Core Data 통계 쿼리",
                "usageScenario": "한 달간 내 휴식 습관이 개선되고 있는지 확인하고 싶을 때",
                "problemSolved": "눈 건강이 나아지는지 체감하기 어려움",
                "userBenefit": "데이터로 습관 개선 확인, 성취감 획득"
            }
        },
        {
            "name": "맞춤형 알림 간격 설정",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "개인화",
                "description": "20분 기본 외에 15분, 30분, 45분 등 원하는 간격으로 조정 가능합니다",
                "userValue": "내 업무 패턴에 맞춰 휴식 타이밍을 최적화할 수 있습니다",
                "technicalNotes": "UserDefaults 설정 저장, 타이머 재구성",
                "usageScenario": "업무 집중 시간이 더 길거나 짧을 때",
                "problemSolved": "고정된 20분이 모든 상황에 맞지 않음",
                "userBenefit": "내 리듬에 맞는 완벽한 휴식 주기"
            }
        },
        {
            "name": "방해 금지 모드",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "유연한 제어",
                "description": "중요한 회의나 작업 중 일시적으로 알림을 끌 수 있습니다",
                "userValue": "긴급한 상황에서도 앱을 완전히 끄지 않고 알림만 일시 정지할 수 있습니다",
                "technicalNotes": "타이머 일시 정지, 알림 스케줄 관리",
                "usageScenario": "중요한 프레젠테이션이나 면접 중일 때",
                "problemSolved": "중요한 순간에 알림이 방해가 됨",
                "userBenefit": "30분, 1시간, 2시간 단위로 스누즈 가능"
            }
        },
        {
            "name": "위젯 지원",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "빠른 확인",
                "description": "홈 화면에서 오늘 휴식 횟수와 다음 휴식까지 남은 시간을 확인합니다",
                "userValue": "앱을 열지 않고도 내 휴식 현황을 한눈에 파악할 수 있습니다",
                "technicalNotes": "WidgetKit, Timeline Provider",
                "usageScenario": "오늘 몇 번 쉬었는지 빠르게 확인하고 싶을 때",
                "problemSolved": "현황 확인하려고 앱을 열어야 함",
                "userBenefit": "잠금 화면에서도 즉시 확인 가능"
            }
        },
        {
            "name": "휴식 중 화면 보호",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "건강 관리",
                "description": "휴식 시간에 화면을 자동으로 어둡게 하거나 초록색 화면을 표시합니다",
                "userValue": "휴식 중 실수로 화면을 보지 않도록 도와줍니다",
                "technicalNotes": "화면 밝기 제어, 풀스크린 오버레이",
                "usageScenario": "휴식 중인데 습관적으로 화면을 보게 될 때",
                "problemSolved": "휴식 시간에도 화면을 보는 습관",
                "userBenefit": "강제 휴식으로 실제 눈 쉼 효과 증대"
            }
        },
        {
            "name": "성취 배지 시스템",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "동기부여",
                "description": "7일 연속, 한 달 100회 등 목표 달성 시 배지를 획득합니다",
                "userValue": "꾸준한 눈 건강 습관에 대한 보상으로 동기부여됩니다",
                "technicalNotes": "업적 시스템, 로컬 저장",
                "usageScenario": "습관을 지속하기 위한 동기가 필요할 때",
                "problemSolved": "단조로운 알림으로 흥미가 떨어짐",
                "userBenefit": "게임처럼 재미있게 눈 건강 관리"
            }
        },
        {
            "name": "다양한 눈 운동 프로그램",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "건강 관리",
                "description": "기본 20-20-20 외에 3분 집중 운동, 5분 완전 휴식 등 다양한 프로그램 제공",
                "userValue": "상황에 맞는 여러 눈 운동 방법을 선택할 수 있습니다",
                "technicalNotes": "운동 프로그램 DB, 가이드 애니메이션",
                "usageScenario": "점심시간에 좀 더 긴 눈 운동을 하고 싶을 때",
                "problemSolved": "한 가지 운동만 반복해서 지루함",
                "userBenefit": "짧은 휴식부터 긴 휴식까지 선택 가능"
            }
        },
        {
            "name": "건강 앱 연동",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "데이터 통합",
                "description": "Apple Health에 마인드풀니스 시간으로 기록됩니다",
                "userValue": "눈 휴식을 건강 데이터의 일부로 추적할 수 있습니다",
                "technicalNotes": "HealthKit 통합",
                "usageScenario": "전반적인 건강 데이터를 통합 관리하고 싶을 때",
                "problemSolved": "눈 건강이 전체 건강 데이터와 분리됨",
                "userBenefit": "건강 앱에서 모든 웰빙 활동 한눈에 확인"
            }
        },
        {
            "name": "팀/그룹 챌린지",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "사회적 동기부여",
                "description": "팀원들과 함께 눈 건강 챌린지에 참여하고 순위를 확인합니다",
                "userValue": "혼자가 아닌 동료들과 함께 건강한 습관을 만들어갑니다",
                "technicalNotes": "서버 연동, 리더보드",
                "usageScenario": "회사 동료들과 함께 눈 건강 캠페인을 할 때",
                "problemSolved": "혼자 하면 작심삼일로 끝남",
                "userBenefit": "동료들과 경쟁하며 재미있게 지속"
            }
        },
        {
            "name": "음성 안내 옵션",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "접근성",
                "description": "눈 운동을 음성으로 안내하여 화면을 보지 않고도 따라할 수 있습니다",
                "userValue": "시각장애가 있거나 눈을 완전히 감고 운동하고 싶을 때 유용합니다",
                "technicalNotes": "AVSpeechSynthesizer, VoiceOver 지원",
                "usageScenario": "눈을 감고 완전히 휴식하면서 운동하고 싶을 때",
                "problemSolved": "화면을 봐야 운동 방법을 알 수 있음",
                "userBenefit": "눈을 감은 채로 음성만 들으며 운동"
            }
        }
    ],

    "probability-calculator": [
        {
            "name": "실생활 확률 템플릿",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "빠른 시작",
                "description": "로또, 가위바위보, 주사위 등 자주 쓰는 확률 계산 템플릿을 제공합니다",
                "userValue": "복잡한 수식 입력 없이 바로 원하는 확률을 계산할 수 있습니다",
                "technicalNotes": "사전 정의된 확률 모델, 파라미터 입력만",
                "usageScenario": "로또 당첨 확률이 궁금할 때",
                "problemSolved": "확률 문제를 수식으로 변환하기 어려움",
                "userBenefit": "3탭으로 원하는 확률 즉시 계산"
            }
        },
        {
            "name": "계산 히스토리",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "기록 관리",
                "description": "이전에 계산했던 확률들을 저장하고 다시 볼 수 있습니다",
                "userValue": "같은 계산을 반복하지 않고 저장된 결과를 바로 확인할 수 있습니다",
                "technicalNotes": "Core Data, 계산 결과 저장",
                "usageScenario": "어제 계산했던 확률을 다시 확인하고 싶을 때",
                "problemSolved": "같은 계산을 매번 다시 해야 함",
                "userBenefit": "과거 계산 즉시 재사용"
            }
        },
        {
            "name": "여러 시나리오 비교",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "의사결정 지원",
                "description": "여러 가지 경우의 확률을 나란히 비교할 수 있습니다",
                "userValue": "A안과 B안 중 어느 것이 더 유리한지 확률로 비교하여 결정할 수 있습니다",
                "technicalNotes": "멀티 계산기, 비교 뷰",
                "usageScenario": "두 가지 선택지 중 확률적으로 유리한 것을 고를 때",
                "problemSolved": "여러 경우를 따로 계산하고 기억해야 함",
                "userBenefit": "한 화면에서 모든 시나리오 확률 비교"
            }
        },
        {
            "name": "확률 분포 그래프",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "직관적 이해",
                "description": "정규분포, 이항분포 등 확률 분포를 그래프로 시각화합니다",
                "userValue": "추상적인 분포 개념을 시각적으로 이해할 수 있습니다",
                "technicalNotes": "통계 차트, 분포 계산 알고리즘",
                "usageScenario": "통계 수업이나 연구에서 분포를 확인할 때",
                "problemSolved": "분포 개념이 수식으로만 있어 이해 어려움",
                "userBenefit": "그래프로 한눈에 분포 파악"
            }
        },
        {
            "name": "학습 모드",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "교육",
                "description": "확률 계산 과정을 단계별로 설명합니다",
                "userValue": "결과뿐만 아니라 어떻게 계산되는지 배울 수 있습니다",
                "technicalNotes": "단계별 풀이 로직, 설명 텍스트",
                "usageScenario": "확률 수업을 듣거나 시험 준비할 때",
                "problemSolved": "답만 알고 과정은 모름",
                "userBenefit": "계산기이면서 동시에 학습 도구"
            }
        },
        {
            "name": "공유 및 내보내기",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "협업",
                "description": "계산 결과를 이미지나 PDF로 저장하거나 공유할 수 있습니다",
                "userValue": "보고서나 과제에 확률 계산 결과를 바로 첨부할 수 있습니다",
                "technicalNotes": "이미지 렌더링, PDF 생성, Share Sheet",
                "usageScenario": "과제나 보고서에 확률 계산을 포함해야 할 때",
                "problemSolved": "스크린샷으로 찍어야 하는 번거로움",
                "userBenefit": "깔끔한 형식으로 결과 공유"
            }
        },
        {
            "name": "단위 변환 도구",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "편의 기능",
                "description": "확률을 백분율, 소수, 분수 등 다양한 형식으로 변환합니다",
                "userValue": "상황에 맞는 표현 방식으로 확률을 이해하고 전달할 수 있습니다",
                "technicalNotes": "수학 변환 함수",
                "usageScenario": "확률을 다른 형식으로 표현해야 할 때",
                "problemSolved": "소수를 백분율로 바꾸는 계산을 따로 해야 함",
                "userBenefit": "모든 형식 동시 표시로 즉시 확인"
            }
        },
        {
            "name": "즐겨찾기 계산",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "빠른 접근",
                "description": "자주 하는 계산을 즐겨찾기에 저장합니다",
                "userValue": "반복적으로 하는 계산을 빠르게 다시 실행할 수 있습니다",
                "technicalNotes": "북마크 시스템",
                "usageScenario": "매주 같은 확률을 계산해야 할 때",
                "problemSolved": "같은 값을 매번 다시 입력",
                "userBenefit": "한 번의 탭으로 자주 쓰는 계산 실행"
            }
        },
        {
            "name": "다크 모드 지원",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "UI 개선",
                "description": "시스템 설정에 따라 자동으로 다크 모드를 적용합니다",
                "userValue": "밤에 사용할 때 눈의 피로를 줄일 수 있습니다",
                "technicalNotes": "다크 모드 컬러셋, 자동 전환",
                "usageScenario": "야간에 앱을 사용할 때",
                "problemSolved": "밝은 화면이 눈부심",
                "userBenefit": "어두운 환경에서 편안한 사용"
            }
        },
        {
            "name": "계산기 모드",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "복잡한 계산",
                "description": "확률 계산에 필요한 조합, 팩토리얼 등을 직접 계산할 수 있는 계산기를 제공합니다",
                "userValue": "다른 계산기 앱을 열지 않고도 중간 계산을 할 수 있습니다",
                "technicalNotes": "내장 계산기 엔진",
                "usageScenario": "확률 계산 중 중간 값을 확인하고 싶을 때",
                "problemSolved": "계산기 앱을 따로 열어야 함",
                "userBenefit": "한 앱 안에서 모든 계산 완료"
            }
        }
    ],

    "rebound-journal": [
        {
            "name": "감정 체크인",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "회복 기록",
                "description": "하루 중 여러 번 현재 감정 상태를 간단히 기록할 수 있습니다",
                "userValue": "하루 종일의 감정 변화를 세밀하게 추적할 수 있습니다",
                "technicalNotes": "빠른 감정 입력 UI, 타임스탬프",
                "usageScenario": "아침, 점심, 저녁 감정이 어떻게 바뀌는지 확인하고 싶을 때",
                "problemSolved": "하루에 한 번만 기록하면 변화를 놓침",
                "userBenefit": "3초 안에 감정 기록 완료"
            }
        },
        {
            "name": "긍정 일기",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "회복 촉진",
                "description": "매일 감사한 일 3가지를 적는 프롬프트를 제공합니다",
                "userValue": "부정적 생각에서 벗어나 긍정적 측면을 찾는 습관을 만듭니다",
                "technicalNotes": "프롬프트 시스템, 일일 알림",
                "usageScenario": "하루를 마무리하며 좋았던 점을 떠올리고 싶을 때",
                "problemSolved": "부정적인 것만 계속 생각하게 됨",
                "userBenefit": "긍정 찾기 습관으로 빠른 회복"
            }
        },
        {
            "name": "트리거 패턴 분석",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "인사이트",
                "description": "감정이 안 좋아지는 상황을 AI가 분석하여 패턴을 찾아줍니다",
                "userValue": "어떤 상황에서 힘들어지는지 객관적으로 파악할 수 있습니다",
                "technicalNotes": "텍스트 분석, 패턴 인식",
                "usageScenario": "왜 자꾸 같은 상황에서 힘들어지는지 궁금할 때",
                "problemSolved": "주관적으로는 패턴을 발견하기 어려움",
                "userBenefit": "트리거를 알면 미리 대비 가능"
            }
        },
        {
            "name": "회복 마일스톤",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "동기부여",
                "description": "7일 연속 기록, 30일 회복 등 주요 단계마다 축하 메시지를 받습니다",
                "userValue": "작은 성취를 인정받으며 계속 나아갈 힘을 얻습니다",
                "technicalNotes": "마일스톤 시스템, 축하 애니메이션",
                "usageScenario": "꾸준히 기록하고 있지만 변화가 느껴지지 않을 때",
                "problemSolved": "노력을 인정받지 못해 포기하게 됨",
                "userBenefit": "단계별 축하로 지속 동기 부여"
            }
        },
        {
            "name": "전문가 콘텐츠",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "회복 지원",
                "description": "심리 전문가의 회복 팁과 가이드를 제공합니다",
                "userValue": "혼자 고민하지 않고 전문적인 조언을 받을 수 있습니다",
                "technicalNotes": "콘텐츠 DB, 상황별 추천",
                "usageScenario": "힘든 상황에서 어떻게 대처해야 할지 모를 때",
                "problemSolved": "전문가 도움이 필요하지만 접근이 어려움",
                "userBenefit": "검증된 회복 전략으로 효과적 대처"
            }
        },
        {
            "name": "사진 일기",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "시각적 기록",
                "description": "감정과 함께 사진을 첨부하여 그날의 순간을 생생하게 기록합니다",
                "userValue": "나중에 돌아봤을 때 그날의 감정이 더 선명하게 떠오릅니다",
                "technicalNotes": "이미지 첨부, 갤러리 통합",
                "usageScenario": "특별한 순간이나 힘들었던 날을 기억하고 싶을 때",
                "problemSolved": "텍스트만으로는 감정을 완전히 담기 어려움",
                "userBenefit": "사진으로 더 풍부한 기억 보존"
            }
        },
        {
            "name": "명상 가이드",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "회복 촉진",
                "description": "5분, 10분 짧은 명상 가이드 오디오를 제공합니다",
                "userValue": "감정이 힘들 때 즉시 명상으로 진정할 수 있습니다",
                "technicalNotes": "오디오 플레이어, 명상 스크립트",
                "usageScenario": "갑자기 불안하거나 우울할 때",
                "problemSolved": "감정이 힘들 때 대처 방법을 모름",
                "userBenefit": "즉시 사용 가능한 진정 도구"
            }
        },
        {
            "name": "비공개 모드",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "프라이버시",
                "description": "Face ID/Touch ID로 앱을 잠그고 민감한 내용을 보호합니다",
                "userValue": "안전하게 솔직한 감정을 기록할 수 있습니다",
                "technicalNotes": "생체 인증, 데이터 암호화",
                "usageScenario": "타인이 내 일기를 볼까 걱정될 때",
                "problemSolved": "남이 볼까봐 솔직하게 못 씀",
                "userBenefit": "완전한 프라이버시로 자유로운 표현"
            }
        },
        {
            "name": "응급 연락망",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "위기 지원",
                "description": "힘들 때 바로 연락할 수 있는 친구나 상담 기관 번호를 저장합니다",
                "userValue": "위기 상황에서 빠르게 도움을 요청할 수 있습니다",
                "technicalNotes": "연락처 저장, 원터치 전화",
                "usageScenario": "혼자서는 감당하기 힘든 순간",
                "problemSolved": "도움이 필요한데 누구에게 연락할지 모름",
                "userBenefit": "한 번의 탭으로 즉시 도움 요청"
            }
        },
        {
            "name": "회복 리마인더",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "습관 형성",
                "description": "매일 같은 시간에 일기 작성 알림을 보냅니다",
                "userValue": "기록하는 습관을 만들어 꾸준한 회복 과정을 유지합니다",
                "technicalNotes": "로컬 알림, 시간 설정",
                "usageScenario": "바쁘다는 핑계로 기록을 잊어버릴 때",
                "problemSolved": "기록 습관을 만들기 어려움",
                "userBenefit": "알림으로 자동 습관 형성"
            }
        }
    ],

    "relax-on": [
        {
            "name": "수면 타이머",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "5.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "수면 지원",
                "description": "설정한 시간 후 자동으로 소리가 꺼지도록 타이머를 설정합니다",
                "userValue": "잠들 때 소리를 틀어놓고 자동으로 꺼지게 할 수 있습니다",
                "technicalNotes": "타이머, 페이드아웃 효과",
                "usageScenario": "자연 소리를 들으며 잠들고 싶을 때",
                "problemSolved": "밤새 소리가 나서 오히려 방해됨",
                "userBenefit": "30분, 1시간 등 설정 후 안심하고 수면"
            }
        },
        {
            "name": "즐겨찾기 프리셋",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "5.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "맞춤 힐링",
                "description": "자주 쓰는 소리 조합을 저장하여 한 번에 불러옵니다",
                "userValue": "매번 소리를 조합하지 않고 저장된 프리셋으로 바로 재생할 수 있습니다",
                "technicalNotes": "프리셋 저장, 빠른 로드",
                "usageScenario": "밤에는 A조합, 공부할 때는 B조합을 쓸 때",
                "problemSolved": "매번 같은 소리를 다시 설정해야 함",
                "userBenefit": "한 탭으로 완벽한 조합 즉시 재생"
            }
        },
        {
            "name": "3D 공간 오디오",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "5.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "몰입 경험",
                "description": "AirPods Pro의 공간 오디오로 더 현실적인 자연 소리를 제공합니다",
                "userValue": "실제 자연 속에 있는 듯한 입체적인 청각 경험을 할 수 있습니다",
                "technicalNotes": "Spatial Audio API, 입체 음향",
                "usageScenario": "완전한 몰입을 원할 때",
                "problemSolved": "평면적인 소리로 현실감이 부족함",
                "userBenefit": "진짜 숲, 바다에 있는 듯한 느낌"
            }
        },
        {
            "name": "시각적 배경",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "5.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "시청각 통합",
                "description": "소리와 어울리는 자연 배경 영상이나 애니메이션을 보여줍니다",
                "userValue": "소리뿐 아니라 시각적으로도 자연을 느낄 수 있습니다",
                "technicalNotes": "비디오 재생, 애니메이션",
                "usageScenario": "소리와 함께 화면도 힐링되는 이미지를 보고 싶을 때",
                "problemSolved": "소리만으로는 몰입이 부족함",
                "userBenefit": "청각과 시각의 완벽한 조화"
            }
        },
        {
            "name": "집중 모드 연동",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "5.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "시스템 통합",
                "description": "iOS 집중 모드와 연동하여 자동으로 소리를 재생합니다",
                "userValue": "일할 때, 잘 때 등 상황별로 자동으로 적절한 소리가 나옵니다",
                "technicalNotes": "Focus Mode API 연동",
                "usageScenario": "업무 집중 모드를 켰을 때 자동으로 백색소음이 나오길 원할 때",
                "problemSolved": "상황마다 앱을 열어서 재생해야 함",
                "userBenefit": "완전 자동화로 신경 쓸 필요 없음"
            }
        },
        {
            "name": "날씨 연동 추천",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "5.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "상황 인식",
                "description": "현재 날씨에 맞는 소리를 추천합니다 (비 오는 날 빗소리 등)",
                "userValue": "날씨와 어울리는 소리로 더 자연스러운 힐링 경험을 할 수 있습니다",
                "technicalNotes": "날씨 API, 상황 인식",
                "usageScenario": "밖에 비가 오는데 집에서도 빗소리를 듣고 싶을 때",
                "problemSolved": "어떤 소리를 들을지 선택하기 어려움",
                "userBenefit": "날씨 맞춤 자동 추천"
            }
        },
        {
            "name": "사용 통계",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "5.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "진행 추적",
                "description": "이번 주 명상 시간, 자주 듣는 소리 등을 시각화합니다",
                "userValue": "내 힐링 습관을 객관적으로 파악할 수 있습니다",
                "technicalNotes": "사용 시간 추적, 차트",
                "usageScenario": "이번 달 얼마나 명상에 시간을 썼는지 궁금할 때",
                "problemSolved": "얼마나 사용하는지 모름",
                "userBenefit": "힐링 시간 시각화로 자기 관리"
            }
        },
        {
            "name": "커뮤니티 추천 믹스",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "5.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "소셜",
                "description": "다른 사용자들이 만든 인기 소리 조합을 탐색하고 사용합니다",
                "userValue": "다른 사람들의 창의적인 조합을 발견하여 새로운 힐링 방법을 찾습니다",
                "technicalNotes": "커뮤니티 기능, 공유 시스템",
                "usageScenario": "새로운 소리 조합을 시도하고 싶을 때",
                "problemSolved": "같은 소리만 반복해서 지루함",
                "userBenefit": "커뮤니티가 검증한 최고의 조합"
            }
        },
        {
            "name": "오프라인 다운로드",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "5.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "오프라인 지원",
                "description": "자주 쓰는 소리를 다운로드하여 인터넷 없이도 재생합니다",
                "userValue": "비행기나 지하철 등 오프라인 환경에서도 자연 소리를 들을 수 있습니다",
                "technicalNotes": "로컬 저장, 다운로드 관리",
                "usageScenario": "해외 여행이나 인터넷이 없는 곳에서 사용할 때",
                "problemSolved": "네트워크 없으면 앱 사용 불가",
                "userBenefit": "언제 어디서나 힐링 가능"
            }
        },
        {
            "name": "Apple Watch 컨트롤",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "5.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "기기 연동",
                "description": "Apple Watch에서 재생, 볼륨, 타이머를 제어합니다",
                "userValue": "침대에 누워서 폰을 꺼내지 않고도 소리를 제어할 수 있습니다",
                "technicalNotes": "watchOS 앱, 동기화",
                "usageScenario": "잠들기 전 편하게 누워서 제어하고 싶을 때",
                "problemSolved": "폰까지 손을 뻗어야 함",
                "userBenefit": "손목에서 모든 제어 가능"
            }
        }
    ],

    "shared-day-designer": [
        {
            "name": "가족 구성원 역할 설정",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "가족 협업",
                "description": "엄마, 아빠, 아이 등 역할을 설정하고 색상으로 구분합니다",
                "userValue": "누구의 일정인지 한눈에 파악할 수 있습니다",
                "technicalNotes": "역할 시스템, 컬러 코딩",
                "usageScenario": "4인 가족의 일정을 한 화면에서 볼 때",
                "problemSolved": "누구 일정인지 구분이 안 됨",
                "userBenefit": "색깔로 즉시 구분"
            }
        },
        {
            "name": "반복 일정 템플릿",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "빠른 입력",
                "description": "매주 월요일 학원, 매일 아침 운동 등 반복 일정을 쉽게 설정합니다",
                "userValue": "같은 일정을 매번 입력하지 않아도 됩니다",
                "technicalNotes": "반복 규칙 엔진",
                "usageScenario": "아이의 정기 학원 일정을 등록할 때",
                "problemSolved": "매주 같은 일정을 일일이 입력",
                "userBenefit": "한 번 설정으로 자동 반복"
            }
        },
        {
            "name": "일정 제안",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "AI 추천",
                "description": "가족 모두가 비는 시간을 찾아 외출이나 모임을 제안합니다",
                "userValue": "언제 가족이 다 같이 시간을 낼 수 있는지 쉽게 찾습니다",
                "technicalNotes": "일정 분석, 빈 시간 탐색",
                "usageScenario": "가족 외식 날짜를 정할 때",
                "problemSolved": "모두의 일정을 비교하며 찾느라 시간 소모",
                "userBenefit": "AI가 최적 시간 자동 제안"
            }
        },
        {
            "name": "할 일 공유",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "작업 관리",
                "description": "장보기, 청소 등 가족 할 일을 등록하고 담당자를 지정합니다",
                "userValue": "집안일을 체계적으로 분담하고 완료 상태를 확인할 수 있습니다",
                "technicalNotes": "TODO 시스템, 담당자 할당",
                "usageScenario": "이번 주 집안일을 가족끼리 나눌 때",
                "problemSolved": "누가 뭘 하기로 했는지 잊어버림",
                "userBenefit": "명확한 역할 분담과 진행 상황 확인"
            }
        },
        {
            "name": "사진 첨부 일정",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "추억 저장",
                "description": "일정에 사진을 첨부하여 그날의 추억을 함께 저장합니다",
                "userValue": "일정뿐 아니라 그날의 순간을 사진으로도 기억할 수 있습니다",
                "technicalNotes": "이미지 첨부, 클라우드 동기화",
                "usageScenario": "가족 여행이나 생일 파티 사진을 일정과 함께 저장할 때",
                "problemSolved": "사진과 일정이 따로 관리됨",
                "userBenefit": "일정 보며 추억도 함께 회상"
            }
        },
        {
            "name": "예산 관리",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "금전 관리",
                "description": "외출이나 행사에 예상 비용을 입력하고 가족 예산을 추적합니다",
                "userValue": "이번 달 가족 활동에 얼마를 쓸지 계획하고 확인할 수 있습니다",
                "technicalNotes": "예산 입력, 지출 합계",
                "usageScenario": "이번 달 외식비를 관리하고 싶을 때",
                "problemSolved": "가족 활동 비용을 파악하기 어려움",
                "userBenefit": "예산 초과 방지, 계획적 소비"
            }
        },
        {
            "name": "위치 공유",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "안전",
                "description": "일정에 위치를 추가하면 가족이 어디 있는지 확인할 수 있습니다",
                "userValue": "아이가 학원에 잘 도착했는지, 배우자가 어디 있는지 안심할 수 있습니다",
                "technicalNotes": "위치 서비스, 지도 통합",
                "usageScenario": "아이가 안전하게 학원에 갔는지 확인할 때",
                "problemSolved": "가족 위치를 모르면 불안함",
                "userBenefit": "실시간 위치로 안심"
            }
        },
        {
            "name": "캘린더 구독",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "통합 관리",
                "description": "학교 일정, 공휴일 등 외부 캘린더를 구독하여 함께 봅니다",
                "userValue": "학사 일정이나 공휴일을 직접 입력하지 않아도 자동으로 표시됩니다",
                "technicalNotes": "iCal 구독, 캘린더 통합",
                "usageScenario": "자녀 학교 일정을 가족 캘린더에 통합할 때",
                "problemSolved": "공휴일이나 학사 일정을 일일이 입력",
                "userBenefit": "자동 동기화로 편리함"
            }
        },
        {
            "name": "월간 리포트",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "회고",
                "description": "이번 달 가족 활동을 정리한 리포트를 생성합니다",
                "userValue": "한 달간 무엇을 했는지 되돌아보며 가족 시간의 질을 점검합니다",
                "technicalNotes": "통계 생성, PDF 리포트",
                "usageScenario": "월말에 이번 달을 돌아보고 싶을 때",
                "problemSolved": "시간이 어떻게 갔는지 실감이 안 남",
                "userBenefit": "가족과 함께한 시간 시각화"
            }
        },
        {
            "name": "긴급 알림",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "안전",
                "description": "긴급 상황을 모든 가족에게 즉시 알립니다",
                "userValue": "응급 상황에서 빠르게 가족에게 알릴 수 있습니다",
                "technicalNotes": "푸시 알림, 우선순위 높음",
                "usageScenario": "아이가 다쳐서 급하게 가족에게 알려야 할 때",
                "problemSolved": "급한 상황에서 일일이 연락하기 어려움",
                "userBenefit": "한 번의 탭으로 모두에게 알림"
            }
        }
    ],

    "bami-log": [
        {
            "name": "육아 일기",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "빠른 기록",
                "description": "아기의 하루를 간단히 기록하고 성장 과정을 문서화합니다",
                "userValue": "바쁜 육아 중에도 30초면 오늘의 특별한 순간을 저장할 수 있습니다",
                "technicalNotes": "빠른 입력 UI, 사진 첨부",
                "usageScenario": "아기가 첫 미소를 지었을 때 바로 기록하고 싶을 때",
                "problemSolved": "특별한 순간을 나중에 기록하려다 잊어버림",
                "userBenefit": "성장 과정을 빠짐없이 기록"
            }
        },
        {
            "name": "수유 트래커",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "건강 관리",
                "description": "수유 시간과 양을 기록하고 패턴을 분석합니다",
                "userValue": "아기가 충분히 먹고 있는지, 수유 간격이 적절한지 확인할 수 있습니다",
                "technicalNotes": "타이머, 통계 차트",
                "usageScenario": "아기가 잘 먹고 있는지 확인하고 싶을 때",
                "problemSolved": "마지막 수유 시간을 기억하기 어려움",
                "userBenefit": "정확한 수유 기록으로 건강 관리"
            }
        },
        {
            "name": "성장 차트",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "성장 추적",
                "description": "키, 몸무게를 입력하면 성장 곡선 차트로 표시합니다",
                "userValue": "아기가 또래에 비해 잘 자라고 있는지 객관적으로 확인할 수 있습니다",
                "technicalNotes": "성장 곡선 알고리즘, 차트",
                "usageScenario": "검진 후 아기 성장이 정상인지 확인할 때",
                "problemSolved": "성장 기록이 산발적이어서 추세 파악 어려움",
                "userBenefit": "WHO 기준 성장 곡선과 비교"
            }
        },
        {
            "name": "예방접종 알림",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "건강 관리",
                "description": "아기 개월 수에 맞는 예방접종 일정을 알려줍니다",
                "userValue": "접종을 놓치지 않고 적기에 맞출 수 있습니다",
                "technicalNotes": "예방접종 일정 DB, 알림",
                "usageScenario": "다음 예방접종이 언제인지 확인할 때",
                "problemSolved": "예방접종 일정을 놓쳐서 늦게 맞춤",
                "userBenefit": "자동 알림으로 적기 접종"
            }
        },
        {
            "name": "수면 패턴 분석",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "생활 패턴",
                "description": "아기의 수면 시간을 기록하고 패턴을 분석합니다",
                "userValue": "언제 재우면 잘 자는지, 수면 시간이 충분한지 파악할 수 있습니다",
                "technicalNotes": "수면 추적, 패턴 분석",
                "usageScenario": "아기가 자주 깨서 수면 패턴을 개선하고 싶을 때",
                "problemSolved": "언제 재우는 게 좋을지 모름",
                "userBenefit": "데이터 기반 수면 루틴 최적화"
            }
        },
        {
            "name": "마일스톤 추적",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "성장 추적",
                "description": "뒤집기, 걷기 등 발달 단계를 체크하고 기록합니다",
                "userValue": "아기의 발달이 정상적으로 진행되는지 확인할 수 있습니다",
                "technicalNotes": "마일스톤 체크리스트",
                "usageScenario": "아기가 또래보다 발달이 느린 건 아닌지 확인할 때",
                "problemSolved": "어떤 발달 단계를 거쳐야 하는지 모름",
                "userBenefit": "월령별 체크리스트로 발달 확인"
            }
        },
        {
            "name": "육아 팁 콘텐츠",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "학습 효율",
                "description": "전문가의 육아 팁과 가이드를 아기 월령에 맞춰 제공합니다",
                "userValue": "검색하지 않아도 필요한 정보가 적시에 제공됩니다",
                "technicalNotes": "콘텐츠 DB, 맞춤 추천",
                "usageScenario": "이유식을 시작할 때가 됐는데 방법을 모를 때",
                "problemSolved": "인터넷에서 정보를 찾느라 시간 소모",
                "userBenefit": "검증된 정보를 딱 필요한 시점에"
            }
        },
        {
            "name": "가족 공유",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "협업",
                "description": "배우자나 할머니와 육아 기록을 공유하고 함께 관리합니다",
                "userValue": "누가 마지막으로 수유했는지, 기저귀를 갈았는지 공유할 수 있습니다",
                "technicalNotes": "iCloud 동기화, 멀티 유저",
                "usageScenario": "배우자와 교대로 육아할 때",
                "problemSolved": "마지막에 뭘 했는지 서로 모름",
                "userBenefit": "실시간 동기화로 완벽한 협업"
            }
        },
        {
            "name": "사진 타임라인",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "추억 저장",
                "description": "아기 사진을 시간 순으로 정리하여 성장 과정을 시각화합니다",
                "userValue": "아기가 얼마나 자랐는지 사진으로 한눈에 확인할 수 있습니다",
                "technicalNotes": "사진 정렬, 타임라인 뷰",
                "usageScenario": "1년간 아기 성장을 사진으로 돌아보고 싶을 때",
                "problemSolved": "사진이 휴대폰에 흩어져 있음",
                "userBenefit": "성장 타임라인으로 감동적인 회상"
            }
        },
        {
            "name": "출산 준비 체크리스트",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "출산 준비",
                "description": "출산 전 준비할 것들을 체크리스트로 제공합니다",
                "userValue": "출산 가방, 서류 등 빠뜨리지 않고 준비할 수 있습니다",
                "technicalNotes": "체크리스트 시스템",
                "usageScenario": "출산이 임박했는데 뭘 준비해야 할지 모를 때",
                "problemSolved": "출산 준비를 체계적으로 하기 어려움",
                "userBenefit": "전문가 검증 체크리스트로 완벽 준비"
            }
        }
    ],

    "daily-compliment": [
        {
            "name": "기분에 맞는 칭찬",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "맞춤 추천",
                "description": "현재 기분을 선택하면 그에 맞는 칭찬을 제공합니다",
                "userValue": "슬플 때는 위로, 기쁠 때는 축하 등 상황에 맞는 메시지를 받습니다",
                "technicalNotes": "감정 선택 UI, 맞춤 메시지",
                "usageScenario": "힘든 하루를 보내고 위로가 필요할 때",
                "problemSolved": "상황과 맞지 않는 칭찬은 공허함",
                "userBenefit": "내 감정에 딱 맞는 칭찬"
            }
        },
        {
            "name": "위젯 지원",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "하루 시작",
                "description": "홈 화면 위젯에서 매일 새로운 칭찬을 바로 볼 수 있습니다",
                "userValue": "앱을 열지 않고도 잠금 화면에서 칭찬을 받을 수 있습니다",
                "technicalNotes": "WidgetKit, 일일 업데이트",
                "usageScenario": "아침에 폰을 켤 때 칭찬을 받고 싶을 때",
                "problemSolved": "앱을 열어야만 칭찬을 볼 수 있음",
                "userBenefit": "잠금 화면에서 즉시 긍정 에너지"
            }
        },
        {
            "name": "친구에게 칭찬 보내기",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "공유하기",
                "description": "받은 칭찬을 친구에게 공유하거나 직접 작성해서 보냅니다",
                "userValue": "주변 사람들에게도 긍정 에너지를 전파할 수 있습니다",
                "technicalNotes": "메시지 작성, Share Sheet",
                "usageScenario": "힘들어하는 친구를 응원하고 싶을 때",
                "problemSolved": "칭찬하고 싶은데 뭐라 할지 모름",
                "userBenefit": "앱이 대신 칭찬 메시지 작성"
            }
        },
        {
            "name": "칭찬 카테고리",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "콘텐츠 다양성",
                "description": "외모, 성격, 능력 등 카테고리별로 칭찬을 분류합니다",
                "userValue": "특정 부분에 대한 칭찬을 골라서 받을 수 있습니다",
                "technicalNotes": "카테고리 필터, 태그 시스템",
                "usageScenario": "오늘은 외모에 자신감이 없어서 외모 칭찬을 듣고 싶을 때",
                "problemSolved": "모든 칭찬이 섞여 있음",
                "userBenefit": "필요한 부분의 칭찬 선택 가능"
            }
        },
        {
            "name": "음성 칭찬",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "몰입 경험",
                "description": "칭찬을 따뜻한 음성으로 들려줍니다",
                "userValue": "글로 읽는 것보다 음성으로 들으면 더 진심이 느껴집니다",
                "technicalNotes": "TTS, 감정 있는 음성",
                "usageScenario": "눈을 감고 칭찬을 들으며 위로받고 싶을 때",
                "problemSolved": "텍스트만으로는 감정 전달이 부족함",
                "userBenefit": "진짜 사람이 칭찬하는 듯한 느낌"
            }
        },
        {
            "name": "칭찬 배지",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "동기부여",
                "description": "7일 연속, 30일 연속 등 달성 시 배지를 획득합니다",
                "userValue": "꾸준히 긍정적인 습관을 유지하는 데 동기가 됩니다",
                "technicalNotes": "스트릭 추적, 배지 시스템",
                "usageScenario": "매일 칭찬을 받는 습관을 만들고 싶을 때",
                "problemSolved": "며칠 하다가 잊어버림",
                "userBenefit": "배지로 지속 동기 부여"
            }
        },
        {
            "name": "나만의 칭찬 추가",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "개인화",
                "description": "직접 칭찬 문구를 작성하고 저장할 수 있습니다",
                "userValue": "내가 듣고 싶은 특별한 칭찬을 만들 수 있습니다",
                "technicalNotes": "사용자 입력, DB 저장",
                "usageScenario": "특정 상황에 필요한 맞춤 칭찬을 만들고 싶을 때",
                "problemSolved": "제공되는 칭찬이 내 상황과 안 맞음",
                "userBenefit": "완전히 나를 위한 칭찬"
            }
        },
        {
            "name": "칭찬 저널",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "감정 회복",
                "description": "매일 받은 칭찬과 함께 그날의 감사한 일을 적습니다",
                "userValue": "칭찬과 감사를 함께 기록하며 긍정적 마인드셋을 강화합니다",
                "technicalNotes": "저널 에디터, 일별 저장",
                "usageScenario": "하루를 긍정적으로 마무리하고 싶을 때",
                "problemSolved": "칭찬만 받고 끝나서 효과가 오래가지 않음",
                "userBenefit": "칭찬 + 감사 조합으로 강력한 긍정 효과"
            }
        },
        {
            "name": "알림 시간 설정",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "습관 형성",
                "description": "원하는 시간에 칭찬 알림을 받도록 설정합니다",
                "userValue": "아침, 점심, 저녁 등 필요한 시간에 칭찬을 받을 수 있습니다",
                "technicalNotes": "로컬 알림, 시간 설정",
                "usageScenario": "출근 전 아침에 칭찬을 받고 하루를 시작하고 싶을 때",
                "problemSolved": "앱을 열 생각을 못 함",
                "userBenefit": "자동 알림으로 매일 칭찬 습관"
            }
        },
        {
            "name": "테마별 칭찬팩",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "콘텐츠 다양성",
                "description": "연애, 직장, 육아 등 상황별 칭찬 팩을 제공합니다",
                "userValue": "내 상황에 딱 맞는 칭찬을 받을 수 있습니다",
                "technicalNotes": "테마 분류, 팩 시스템",
                "usageScenario": "육아로 힘들 때 엄마/아빠를 위한 칭찬을 받고 싶을 때",
                "problemSolved": "일반적인 칭찬은 공감이 안 됨",
                "userBenefit": "내 상황에 공감하는 맞춤 칭찬"
            }
        }
    ],

    "donkko-mart": [
        {
            "name": "자동 카테고리 분류",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "정리와 분류",
                "description": "물건을 입력하면 자동으로 채소, 육류, 생활용품 등으로 분류합니다",
                "userValue": "마트에서 동선에 맞춰 효율적으로 장을 볼 수 있습니다",
                "technicalNotes": "자동 분류 알고리즘, 카테고리 DB",
                "usageScenario": "마트에서 이리저리 왔다갔다 하지 않고 한 번에 장보고 싶을 때",
                "problemSolved": "물건 순서가 뒤죽박죽이라 마트를 여러 번 왕복",
                "userBenefit": "동선 최적화로 장보기 시간 30% 단축"
            }
        },
        {
            "name": "음성 입력",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "빠른 입력",
                "description": "말로 물건 이름을 불러서 목록에 추가합니다",
                "userValue": "요리 중이나 바쁠 때 손을 쓰지 않고도 목록을 만들 수 있습니다",
                "technicalNotes": "음성 인식, Siri 통합",
                "usageScenario": "요리하다가 재료가 떨어진 걸 발견했을 때",
                "problemSolved": "손이 더러운 상태에서 폰을 만질 수 없음",
                "userBenefit": "말만으로 즉시 추가"
            }
        },
        {
            "name": "가격 입력 및 예산 관리",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "금전 관리",
                "description": "물건별 예상 가격을 입력하고 총액을 실시간으로 확인합니다",
                "userValue": "예산 초과 없이 계획적으로 장을 볼 수 있습니다",
                "technicalNotes": "가격 입력, 합계 계산",
                "usageScenario": "이번 달 장보기 예산이 정해져 있을 때",
                "problemSolved": "계산대에서 예상보다 많이 나와 당황",
                "userBenefit": "실시간 합계로 예산 내 쇼핑"
            }
        },
        {
            "name": "자주 사는 물건 즐겨찾기",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "빠른 입력",
                "description": "매번 사는 우유, 계란 등을 즐겨찾기에 저장하여 빠르게 추가합니다",
                "userValue": "반복적으로 같은 물건을 타이핑하지 않아도 됩니다",
                "technicalNotes": "북마크 시스템, 빈도 분석",
                "usageScenario": "주간 장보기 때마다 같은 물건을 살 때",
                "problemSolved": "매주 같은 물건을 일일이 입력",
                "userBenefit": "한 탭으로 자주 사는 물건 추가"
            }
        },
        {
            "name": "장보기 히스토리",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "기록 관리",
                "description": "지난주, 지난달 뭘 샀는지 기록을 확인하고 재사용합니다",
                "userValue": "저번에 뭘 샀는지 참고하여 빠뜨리지 않고 장을 볼 수 있습니다",
                "technicalNotes": "히스토리 저장, 재사용 기능",
                "usageScenario": "지난주 목록을 그대로 다시 쓰고 싶을 때",
                "problemSolved": "뭘 샀는지 기억이 안 나서 중복 구매나 누락",
                "userBenefit": "과거 목록 복사로 빠른 작성"
            }
        },
        {
            "name": "가족 공유 목록",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "협업",
                "description": "가족이 같은 장보기 목록을 실시간으로 공유하고 편집합니다",
                "userValue": "엄마가 집에서 추가한 물건을 아빠가 마트에서 즉시 확인할 수 있습니다",
                "technicalNotes": "iCloud 동기화, 실시간 업데이트",
                "usageScenario": "가족 중 누가 마트에 가든 같은 목록을 보고 싶을 때",
                "problemSolved": "누가 뭘 사기로 했는지 모름",
                "userBenefit": "실시간 동기화로 완벽한 협업"
            }
        },
        {
            "name": "마트 위치 알림",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "위치 기반",
                "description": "등록한 마트 근처에 오면 장보기 목록을 알림으로 띄워줍니다",
                "userValue": "마트 앞을 지나갈 때 장볼 것을 상기시켜줍니다",
                "technicalNotes": "지오펜싱, 위치 기반 알림",
                "usageScenario": "퇴근길에 마트 앞을 지날 때 장보는 걸 잊고 지나칠 때",
                "problemSolved": "마트 앞을 지나가고 집에 가서야 생각남",
                "userBenefit": "자동 알림으로 절대 놓치지 않음"
            }
        },
        {
            "name": "레시피 연동",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "요리 지원",
                "description": "만들고 싶은 요리의 재료를 한 번에 목록에 추가합니다",
                "userValue": "레시피 보고 재료를 일일이 적지 않아도 됩니다",
                "technicalNotes": "레시피 파싱, 재료 추출",
                "usageScenario": "새로운 요리를 만들려고 레시피를 볼 때",
                "problemSolved": "레시피 재료를 하나씩 옮겨 적는 번거로움",
                "userBenefit": "레시피 링크 붙여넣기로 자동 추가"
            }
        },
        {
            "name": "구매 체크 애니메이션",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "사용 편의성",
                "description": "물건을 담으면 만족스러운 체크 애니메이션과 햅틱을 제공합니다",
                "userValue": "장보는 과정이 더 즐겁고 만족스러워집니다",
                "technicalNotes": "애니메이션, 햅틱 피드백",
                "usageScenario": "마트에서 물건을 카트에 담을 때마다 체크할 때",
                "problemSolved": "단조로운 체크 동작",
                "userBenefit": "기분 좋은 피드백으로 즐거운 쇼핑"
            }
        },
        {
            "name": "마트별 가격 비교",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "금전 관리",
                "description": "같은 물건의 가격을 여러 마트에서 비교하여 보여줍니다",
                "userValue": "어느 마트가 더 저렴한지 한눈에 확인하고 결정할 수 있습니다",
                "technicalNotes": "가격 DB, 비교 UI",
                "usageScenario": "A마트와 B마트 중 어디가 저렴한지 확인하고 싶을 때",
                "problemSolved": "어디가 싼지 모르고 그냥 가까운 곳으로",
                "userBenefit": "가격 비교로 절약"
            }
        }
    ],

    "pixel-mimi": [
        {
            "name": "레이어 시스템",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "고급 편집",
                "description": "여러 레이어를 만들어 복잡한 픽셀 아트를 작업할 수 있습니다",
                "userValue": "배경과 캐릭터를 분리하여 더 전문적인 작품을 만들 수 있습니다",
                "technicalNotes": "레이어 관리, 순서 변경",
                "usageScenario": "복잡한 씬을 그릴 때 요소별로 분리하고 싶을 때",
                "problemSolved": "모든 것을 한 레이어에 그려서 수정이 어려움",
                "userBenefit": "레이어별 편집으로 작업 효율 대폭 향상"
            }
        },
        {
            "name": "애니메이션 프레임",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "창작 확장",
                "description": "여러 프레임을 그려 움직이는 픽셀 아트를 만들 수 있습니다",
                "userValue": "정적인 그림을 넘어 애니메이션 작품을 만들 수 있습니다",
                "technicalNotes": "프레임 관리, 재생 기능, GIF 내보내기",
                "usageScenario": "캐릭터가 걷는 애니메이션을 만들고 싶을 때",
                "problemSolved": "정지 이미지만 가능",
                "userBenefit": "움직이는 픽셀 아트로 표현력 극대화"
            }
        },
        {
            "name": "대칭 그리기 모드",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "편의 도구",
                "description": "한쪽을 그리면 반대편도 자동으로 그려집니다",
                "userValue": "대칭 캐릭터를 쉽게 그릴 수 있습니다",
                "technicalNotes": "미러링 알고리즘",
                "usageScenario": "정면 얼굴이나 대칭 디자인을 그릴 때",
                "problemSolved": "양쪽을 똑같이 그리기 어려움",
                "userBenefit": "절반만 그려도 완벽한 대칭"
            }
        },
        {
            "name": "드로잉 도구 확장",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "자유로운 창작",
                "description": "연필, 선, 원, 사각형, 채우기 등 다양한 도구를 제공합니다",
                "userValue": "복잡한 형태를 빠르게 그릴 수 있습니다",
                "technicalNotes": "도형 도구, 채우기 알고리즘",
                "usageScenario": "큰 영역을 한 색으로 채우고 싶을 때",
                "problemSolved": "픽셀 하나씩 찍어서 시간이 오래 걸림",
                "userBenefit": "도구로 빠르고 정확한 작업"
            }
        },
        {
            "name": "프로젝트 저장 및 불러오기",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "작업 관리",
                "description": "작업 중인 그림을 저장하고 나중에 다시 편집할 수 있습니다",
                "userValue": "한 번에 완성하지 않아도 언제든 이어서 작업할 수 있습니다",
                "technicalNotes": "프로젝트 파일 저장, Core Data",
                "usageScenario": "시간이 없어서 나중에 마저 그리고 싶을 때",
                "problemSolved": "한 번 나가면 작업이 사라짐",
                "userBenefit": "여러 프로젝트 관리 가능"
            }
        },
        {
            "name": "템플릿 갤러리",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "빠른 시작",
                "description": "기본 캐릭터, 배경 템플릿을 제공하여 수정해서 사용할 수 있습니다",
                "userValue": "빈 캔버스가 막막하지 않고 템플릿을 기반으로 시작할 수 있습니다",
                "technicalNotes": "템플릿 DB, 불러오기",
                "usageScenario": "픽셀 아트를 처음 그려봐서 어떻게 시작할지 모를 때",
                "problemSolved": "빈 화면 앞에서 막막함",
                "userBenefit": "템플릿 수정으로 쉬운 시작"
            }
        },
        {
            "name": "공유 및 내보내기 옵션",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "공유하기",
                "description": "PNG, GIF 등 다양한 형식으로 내보내고 SNS에 공유합니다",
                "userValue": "완성작을 친구들에게 자랑하거나 SNS에 올릴 수 있습니다",
                "technicalNotes": "이미지 내보내기, Share Sheet",
                "usageScenario": "완성한 픽셀 아트를 인스타그램에 올리고 싶을 때",
                "problemSolved": "작품을 저장만 하고 공유하기 어려움",
                "userBenefit": "다양한 형식으로 내보내기"
            }
        },
        {
            "name": "실행 취소/다시 실행",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "편의 도구",
                "description": "잘못 그린 부분을 되돌리거나 다시 실행할 수 있습니다",
                "userValue": "실수를 두려워하지 않고 자유롭게 그릴 수 있습니다",
                "technicalNotes": "Undo/Redo 스택",
                "usageScenario": "실수로 잘못 칠했을 때",
                "problemSolved": "한 번 잘못 그리면 처음부터 다시",
                "userBenefit": "무한 실행 취소로 안심하고 작업"
            }
        },
        {
            "name": "그리드 표시 옵션",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "시각적 보조",
                "description": "픽셀 그리드 선을 켜거나 끌 수 있습니다",
                "userValue": "그리드 없이 완성작의 실제 모습을 확인할 수 있습니다",
                "technicalNotes": "그리드 토글",
                "usageScenario": "완성된 작품이 어떻게 보일지 확인하고 싶을 때",
                "problemSolved": "그리드 선 때문에 최종 결과물 확인 어려움",
                "userBenefit": "그리드 on/off로 작업과 미리보기 전환"
            }
        },
        {
            "name": "커뮤니티 갤러리",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "영감과 학습",
                "description": "다른 사용자의 작품을 구경하고 영감을 얻습니다",
                "userValue": "다른 사람들의 작품을 보며 아이디어를 얻고 배울 수 있습니다",
                "technicalNotes": "커뮤니티 기능, 작품 업로드",
                "usageScenario": "뭘 그릴지 아이디어가 필요할 때",
                "problemSolved": "혼자 그리면 영감이 부족함",
                "userBenefit": "커뮤니티에서 영감과 동기 부여"
            }
        }
    ],

    "quiz": [
        {
            "name": "카테고리별 퀴즈",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "콘텐츠 다양성",
                "description": "역사, 과학, 영화 등 다양한 카테고리의 퀴즈를 제공합니다",
                "userValue": "관심 있는 주제의 퀴즈를 선택해서 풀 수 있습니다",
                "technicalNotes": "카테고리 필터, 퀴즈 DB",
                "usageScenario": "영화에 대한 퀴즈만 풀고 싶을 때",
                "problemSolved": "모든 주제가 섞여 있어서 원하는 것 찾기 어려움",
                "userBenefit": "관심 분야 집중 학습"
            }
        },
        {
            "name": "난이도 선택",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "맞춤 경험",
                "description": "초급, 중급, 고급 난이도를 선택할 수 있습니다",
                "userValue": "내 수준에 맞는 문제를 풀어 적절한 도전감을 느낄 수 있습니다",
                "technicalNotes": "난이도 태그, 필터링",
                "usageScenario": "너무 어렵거나 쉬운 문제는 재미없을 때",
                "problemSolved": "문제가 너무 쉽거나 어려워서 흥미 상실",
                "userBenefit": "내 수준에 딱 맞는 도전"
            }
        },
        {
            "name": "타이머 챌린지",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "재미있는 학습",
                "description": "제한 시간 내에 문제를 풀어 긴장감을 더합니다",
                "userValue": "시간 압박으로 더 집중하고 긴장감 있게 즐길 수 있습니다",
                "technicalNotes": "카운트다운 타이머",
                "usageScenario": "친구와 누가 더 빨리 푸나 경쟁할 때",
                "problemSolved": "시간 제한 없으면 긴장감 부족",
                "userBenefit": "스릴 있는 퀴즈 경험"
            }
        },
        {
            "name": "성적 통계",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "진행 추적",
                "description": "정답률, 카테고리별 강약점 등을 그래프로 보여줍니다",
                "userValue": "어떤 분야가 약한지 파악하고 집중 학습할 수 있습니다",
                "technicalNotes": "통계 분석, 차트",
                "usageScenario": "내가 어떤 주제에 약한지 확인하고 싶을 때",
                "problemSolved": "강약점을 모르고 무작정 풀기만 함",
                "userBenefit": "데이터 기반 학습 전략"
            }
        },
        {
            "name": "친구와 대결",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "소셜",
                "description": "친구를 초대하여 같은 퀴즈를 풀고 점수를 비교합니다",
                "userValue": "혼자가 아닌 친구와 경쟁하며 더 재미있게 즐길 수 있습니다",
                "technicalNotes": "멀티플레이어, 리더보드",
                "usageScenario": "친구와 누가 더 똑똑한지 겨루고 싶을 때",
                "problemSolved": "혼자 푸는 건 금방 지루함",
                "userBenefit": "친구와 경쟁으로 동기 부여"
            }
        },
        {
            "name": "오답 노트",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "학습 효율",
                "description": "틀린 문제만 모아서 다시 풀 수 있습니다",
                "userValue": "약한 부분을 집중적으로 복습하여 실력을 키울 수 있습니다",
                "technicalNotes": "오답 저장, 필터링",
                "usageScenario": "시험 전 틀린 문제만 다시 보고 싶을 때",
                "problemSolved": "같은 문제를 반복해서 틀림",
                "userBenefit": "약점 집중 공략으로 빠른 향상"
            }
        },
        {
            "name": "일일 챌린지",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "습관 형성",
                "description": "매일 새로운 퀴즈 세트가 제공되어 꾸준히 학습합니다",
                "userValue": "매일 조금씩 풀며 지식을 쌓는 습관을 만들 수 있습니다",
                "technicalNotes": "일일 퀴즈 생성, 스트릭 추적",
                "usageScenario": "매일 조금씩 공부하고 싶을 때",
                "problemSolved": "가끔 한 번씩만 하고 잊어버림",
                "userBenefit": "일일 챌린지로 습관 형성"
            }
        },
        {
            "name": "힌트 시스템",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "학습 지원",
                "description": "모르는 문제에 힌트를 사용할 수 있습니다",
                "userValue": "완전히 모르는 문제도 힌트로 배울 기회를 얻습니다",
                "technicalNotes": "힌트 DB, 포인트 차감",
                "usageScenario": "어려운 문제를 그냥 넘기기 아까울 때",
                "problemSolved": "모르면 그냥 틀리고 끝",
                "userBenefit": "힌트로 학습 효과 증대"
            }
        },
        {
            "name": "해설 및 참고 자료",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "교육",
                "description": "정답 후 자세한 해설과 추가 정보를 제공합니다",
                "userValue": "정답만 알고 끝나는 게 아니라 배경 지식까지 습득합니다",
                "technicalNotes": "해설 DB, 링크 연결",
                "usageScenario": "왜 이게 정답인지 더 알고 싶을 때",
                "problemSolved": "정답만 보고 이유는 모름",
                "userBenefit": "깊이 있는 학습"
            }
        },
        {
            "name": "배지 및 업적",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "동기부여",
                "description": "100문제 달성, 역사 마스터 등 업적을 달성하면 배지를 받습니다",
                "userValue": "성취감을 느끼며 계속 퀴즈를 풀고 싶어집니다",
                "technicalNotes": "업적 시스템, 배지 UI",
                "usageScenario": "목표를 세우고 달성하고 싶을 때",
                "problemSolved": "명확한 목표가 없어서 동기 부족",
                "userBenefit": "배지 수집으로 지속 동기"
            }
        }
    ],

    "schedule-assistant": [
        {
            "name": "작업 우선순위 자동 정렬",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "AI 추천",
                "description": "마감일, 중요도를 고려하여 오늘 할 일 순서를 자동으로 정렬합니다",
                "userValue": "어떤 일부터 해야 할지 고민하지 않고 추천 순서대로 실행하면 됩니다",
                "technicalNotes": "우선순위 알고리즘, 자동 정렬",
                "usageScenario": "할 일이 많은데 뭐부터 할지 모를 때",
                "problemSolved": "우선순위를 정하느라 시간 낭비",
                "userBenefit": "AI가 최적 순서 제시"
            }
        },
        {
            "name": "시간 블록 설정",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "시간 관리",
                "description": "작업에 예상 소요 시간을 입력하면 캘린더에 블록으로 표시합니다",
                "userValue": "하루 일정을 시각적으로 파악하고 현실적으로 계획할 수 있습니다",
                "technicalNotes": "시간 블록 UI, 캘린더 연동",
                "usageScenario": "오늘 할 일들이 시간 내에 끝날지 확인하고 싶을 때",
                "problemSolved": "일정을 너무 빡빡하게 잡아서 실패",
                "userBenefit": "시각적 시간 관리로 현실적 계획"
            }
        },
        {
            "name": "루틴 템플릿",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "습관 형성",
                "description": "아침 루틴, 저녁 루틴 등 반복되는 작업을 템플릿으로 저장합니다",
                "userValue": "매일 하는 일을 일일이 입력하지 않아도 됩니다",
                "technicalNotes": "템플릿 시스템, 자동 추가",
                "usageScenario": "아침마다 운동, 명상, 아침식사 등을 할 때",
                "problemSolved": "매일 같은 작업을 반복 입력",
                "userBenefit": "한 번 설정으로 자동 반복"
            }
        },
        {
            "name": "에너지 레벨 고려",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "AI 추천",
                "description": "오전에는 중요한 일, 오후에는 가벼운 일 등 에너지 패턴을 학습합니다",
                "userValue": "집중력이 높을 때 중요한 일을 하고 효율을 극대화합니다",
                "technicalNotes": "사용 패턴 학습, 시간대별 추천",
                "usageScenario": "오후만 되면 집중력이 떨어질 때",
                "problemSolved": "피곤할 때 어려운 일을 해서 비효율적",
                "userBenefit": "에너지 최적 배분으로 생산성 향상"
            }
        },
        {
            "name": "목표 추적",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "진행 추적",
                "description": "장기 목표를 설정하고 주간/월간 진행 상황을 확인합니다",
                "userValue": "큰 목표를 향해 얼마나 나아가고 있는지 시각적으로 확인할 수 있습니다",
                "technicalNotes": "목표 시스템, 진행률 차트",
                "usageScenario": "올해 목표가 잘 진행되고 있는지 확인하고 싶을 때",
                "problemSolved": "일상에 치여 큰 목표를 잊어버림",
                "userBenefit": "목표 진행률 시각화로 동기 유지"
            }
        },
        {
            "name": "휴식 시간 자동 배치",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "웰빙",
                "description": "작업 사이에 5분, 10분 휴식을 자동으로 배치합니다",
                "userValue": "번아웃 없이 지속 가능한 페이스로 일할 수 있습니다",
                "technicalNotes": "휴식 시간 알고리즘",
                "usageScenario": "쉬지 않고 일하다가 지쳐버릴 때",
                "problemSolved": "휴식 없이 일해서 오히려 비효율적",
                "userBenefit": "규칙적 휴식으로 지속 가능한 생산성"
            }
        },
        {
            "name": "이동 시간 자동 계산",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "통합 관리",
                "description": "일정에 위치가 있으면 이동 시간을 자동으로 계산하여 알립니다",
                "userValue": "약속에 늦지 않도록 언제 출발해야 하는지 알려줍니다",
                "technicalNotes": "지도 API, 교통 상황 반영",
                "usageScenario": "회의 장소가 멀어서 언제 출발해야 할지 모를 때",
                "problemSolved": "이동 시간을 잊고 늦음",
                "userBenefit": "출발 시간 자동 알림"
            }
        },
        {
            "name": "주간 리뷰",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "회고",
                "description": "일주일 동안 뭘 했는지, 얼마나 달성했는지 요약 리포트를 생성합니다",
                "userValue": "한 주를 돌아보며 잘한 점과 개선할 점을 파악합니다",
                "technicalNotes": "통계 생성, 리포트 UI",
                "usageScenario": "주말에 이번 주를 돌아보고 싶을 때",
                "problemSolved": "시간이 어떻게 갔는지 모름",
                "userBenefit": "데이터 기반 자기 성찰"
            }
        },
        {
            "name": "협업 작업 공유",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "통합 관리",
                "description": "팀원과 작업을 공유하고 진행 상황을 실시간으로 확인합니다",
                "userValue": "누가 무엇을 하고 있는지 파악하여 협업이 원활해집니다",
                "technicalNotes": "클라우드 동기화, 멀티 유저",
                "usageScenario": "팀 프로젝트를 관리할 때",
                "problemSolved": "팀원들의 진행 상황을 모름",
                "userBenefit": "투명한 협업 관리"
            }
        },
        {
            "name": "포커스 모드",
            "status": "todo",
            "targetDate": None,
            "targetVersion": "2.0.0",
            "labels": ["feature"],
            "featureMetadata": {
                "category": "집중 지원",
                "description": "현재 작업에만 집중하도록 다른 작업을 숨기고 타이머를 시작합니다",
                "userValue": "멀티태스킹의 유혹 없이 하나의 작업에 몰입할 수 있습니다",
                "technicalNotes": "포커스 UI, 타이머",
                "usageScenario": "중요한 작업에 집중하고 싶을 때",
                "problemSolved": "다른 작업들이 신경 쓰여서 집중 불가",
                "userBenefit": "완벽한 집중 환경"
            }
        }
    ]
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
    backup_file = app_file.with_suffix('.json.backup-upgrade')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original)

    # 저장
    with open(app_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_features_to_app(app_id, features):
    """앱에 새로운 feature 추가"""
    app_file = APPS_DIR / f"{app_id}.json"

    if not app_file.exists():
        print(f"⚠ {app_id}: 파일을 찾을 수 없습니다")
        return 0

    data = load_app_json(app_file)
    app_name = data.get('name', app_id)

    # 기존 태스크 이름들
    existing_tasks = {task['name'] for task in data.get('allTasks', [])}

    # 중복되지 않는 feature만 추가
    new_features = [f for f in features if f['name'] not in existing_tasks]

    if not new_features:
        print(f"ℹ️  {app_name}: 이미 모든 feature가 존재합니다")
        return 0

    # allTasks에 추가
    data['allTasks'].extend(new_features)

    # stats 업데이트
    total_tasks = len(data['allTasks'])
    done = sum(1 for task in data['allTasks'] if task.get('status') == 'done')
    in_progress = sum(1 for task in data['allTasks'] if task.get('status') == 'in-progress')
    todo = sum(1 for task in data['allTasks'] if task.get('status') == 'todo')
    not_started = sum(1 for task in data['allTasks'] if task.get('status') == 'not-started')

    data['stats'] = {
        'done': done,
        'inProgress': in_progress,
        'todo': todo,
        'notStarted': not_started,
        'totalTasks': total_tasks
    }

    save_app_json(app_file, data)
    print(f"✅ {app_name}: {len(new_features)}개 feature 추가 (총 {total_tasks}개)")
    return len(new_features)


def main():
    """메인 실행"""
    print("=" * 80)
    print("11개 앱을 클립키보드 수준으로 업그레이드")
    print("각 앱마다 8-10개 feature 추가")
    print("=" * 80)
    print()

    total_added = 0

    for app_id, features in NEW_FEATURES.items():
        count = add_features_to_app(app_id, features)
        total_added += count

    print()
    print("=" * 80)
    print(f"총 {total_added}개 feature 추가 완료")
    print()
    print("각 feature에 포함된 정보:")
    print("  - category: 사용자 중심 카테고리")
    print("  - description: 무엇을 할 수 있는가")
    print("  - userValue: 왜 유용한가")
    print("  - technicalNotes: 기술 구현")
    print("  - usageScenario: 언제 사용하는가")
    print("  - problemSolved: 어떤 문제 해결")
    print("  - userBenefit: 구체적 이득")
    print("=" * 80)


if __name__ == "__main__":
    main()

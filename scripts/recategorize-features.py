#!/usr/bin/env python3
"""
20년차 기획자 관점에서 feature를 사용자 중심 카테고리로 재분류
"""

import json
from pathlib import Path

APPS_DIR = Path("/Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO/Data/apps")

# 각 앱별 feature 재분류 맵
# {앱ID: {태스크명: {새로운 카테고리, 상세 설명, 사용 시나리오, 해결하는 문제}}}
FEATURE_RECATEGORIZATION = {
    "clip-keyboard": {
        "템플릿 기능 추가": {
            "category": "빠른 입력",
            "usageScenario": "업무 중 자주 쓰는 문구를 매번 타이핑하는 상황",
            "problemSolved": "반복적인 타이핑으로 인한 시간 낭비와 오타 발생",
            "userBenefit": "한 번의 탭으로 긴 문장 입력, 일일 평균 5-10분 절약"
        },
        "아이 클라우드로 메모 동기화": {
            "category": "기기 간 연동",
            "usageScenario": "iPhone에서 저장한 템플릿을 iPad에서도 사용하고 싶을 때",
            "problemSolved": "기기마다 템플릿을 따로 등록해야 하는 번거로움",
            "userBenefit": "어떤 기기에서든 동일한 템플릿 사용 가능"
        },
        "백업 복원 하는 기능": {
            "category": "데이터 안전",
            "usageScenario": "새 아이폰으로 기기 변경 시",
            "problemSolved": "템플릿을 새로 만들어야 하는 불편함",
            "userBenefit": "한 번에 모든 템플릿 복원, 데이터 손실 걱정 없음"
        },
        "faceID로 보안": {
            "category": "데이터 안전",
            "usageScenario": "비밀번호, 계좌번호 등 민감 정보를 템플릿으로 사용할 때",
            "problemSolved": "남이 내 핸드폰을 봤을 때 민감 정보 노출 우려",
            "userBenefit": "생체 인증으로 안전하게 민감 정보 관리"
        },
        "기본 템플릿 제공해주기": {
            "category": "시작 지원",
            "usageScenario": "앱을 처음 설치하고 어떤 템플릿을 만들지 모를 때",
            "problemSolved": "빈 화면에서 시작하는 막막함",
            "userBenefit": "바로 사용 가능한 예시 템플릿으로 빠른 시작"
        },
        "카테고리 관리": {
            "category": "정리와 분류",
            "usageScenario": "템플릿이 많아져서 찾기 어려울 때",
            "problemSolved": "원하는 템플릿을 찾는데 시간이 오래 걸림",
            "userBenefit": "업무용, 개인용 등으로 분류하여 빠른 검색"
        },
        "통계 기능": {
            "category": "절약 시간 확인",
            "usageScenario": "내가 얼마나 시간을 절약했는지 궁금할 때",
            "problemSolved": "앱 사용 효과를 체감하기 어려움",
            "userBenefit": "절약한 시간을 숫자로 확인하며 성취감 획득"
        },
        "맥 OS에서 동작하게 하기": {
            "category": "플랫폼 확장",
            "usageScenario": "맥북에서 작업할 때도 템플릿을 쓰고 싶을 때",
            "problemSolved": "모바일에서만 사용 가능한 한계",
            "userBenefit": "맥에서도 동일한 템플릿 사용으로 업무 효율 증대"
        },
        "붙여넣기 안내 설정 도와주기": {
            "category": "시작 지원",
            "usageScenario": "키보드 권한 설정이 처음이라 방법을 모를 때",
            "problemSolved": "설정 방법을 몰라 앱을 사용하지 못함",
            "userBenefit": "친절한 가이드로 3분 안에 설정 완료"
        },
        "키보드 표시명 중복 제거": {
            "category": "편의성 개선",
            "usageScenario": "키보드 선택 메뉴에서 클립키보드가 여러 개 보일 때",
            "problemSolved": "어떤 키보드를 선택해야 할지 혼란",
            "userBenefit": "깔끔한 키보드 목록으로 빠른 선택"
        },
        "템플릿 관리 개선": {
            "category": "정리와 분류",
            "usageScenario": "템플릿을 수정하거나 삭제하고 싶을 때",
            "problemSolved": "템플릿 편집이 직관적이지 않음",
            "userBenefit": "스와이프로 간편하게 편집/삭제"
        },
        "통계 대시보드": {
            "category": "절약 시간 확인",
            "usageScenario": "월별, 주별로 사용 패턴을 확인하고 싶을 때",
            "problemSolved": "어떤 템플릿을 자주 쓰는지 모름",
            "userBenefit": "사용 빈도 분석으로 효율적인 템플릿 관리"
        },
        "위젯 지원": {
            "category": "빠른 입력",
            "usageScenario": "앱을 열지 않고 바로 템플릿을 복사하고 싶을 때",
            "problemSolved": "앱 실행 → 템플릿 선택 → 복사의 번거로움",
            "userBenefit": "홈 화면에서 즉시 템플릿 복사"
        }
    },

    "three-meals": {
        "식단 피드백 작성기능 추가": {
            "category": "식사 기록",
            "usageScenario": "식사 후 어떤 느낌이었는지 메모하고 싶을 때",
            "problemSolved": "사진만으로는 그 때의 느낌을 기억하기 어려움",
            "userBenefit": "나중에 같은 메뉴를 먹을지 판단하는 근거 마련"
        },
        "좀 더 나은 운동 디자인으로 바꾸기": {
            "category": "활동 기록",
            "usageScenario": "운동 정보를 기록하고 싶을 때",
            "problemSolved": "운동 화면이 직관적이지 않음",
            "userBenefit": "쉽고 빠르게 운동 기록 완료"
        },
        "설정 바로반응": {
            "category": "편의성 개선",
            "usageScenario": "설정을 바꿨는데 앱을 재시작해야 할 때",
            "problemSolved": "설정 변경 후 즉시 확인이 안 됨",
            "userBenefit": "설정 변경 즉시 반영으로 빠른 확인"
        },
        "이미 가지고 있는 추출한 재료로 줄 수 있는 정보": {
            "category": "영양 분석",
            "usageScenario": "내가 먹은 음식의 영양소가 궁금할 때",
            "problemSolved": "식단 사진만 있고 영양 정보는 모름",
            "userBenefit": "칼로리, 단백질 등 영양 정보 자동 분석"
        },
        "유저가 달 성할 수 있는 목표와 앱의 목표 명확하게 하기": {
            "category": "목표 관리",
            "usageScenario": "다이어트 목표를 세우고 진행 상황을 확인할 때",
            "problemSolved": "내 목표와 앱 추천이 섞여서 혼란스러움",
            "userBenefit": "내 목표에 집중하며 명확한 진행 상황 파악"
        },
        "추출한 식단을 바탕으로 이런거 먹으면 좋아 추천하기": {
            "category": "맞춤 추천",
            "usageScenario": "부족한 영양소를 채우고 싶을 때",
            "problemSolved": "무엇을 먹어야 균형잡힌 식단인지 모름",
            "userBenefit": "AI 기반 식단 추천으로 건강한 선택"
        },
        "사실은 오해하고있을 식단에 대한 정보와 팁": {
            "category": "건강 정보",
            "usageScenario": "잘못된 다이어트 상식을 가지고 있을 때",
            "problemSolved": "인터넷의 잘못된 정보로 건강 악화",
            "userBenefit": "전문가 검증된 식단 정보로 올바른 습관 형성"
        },
        "사용자의 식단분석 보이기 감추기 토글 설정 + 이미지 작아지지 않게하기": {
            "category": "화면 설정",
            "usageScenario": "분석 정보 없이 사진만 크게 보고 싶을 때",
            "problemSolved": "분석 정보가 화면을 차지해서 사진이 작음",
            "userBenefit": "원하는 정보만 선택하여 깔끔한 화면"
        },
        "간식 감추는 설정": {
            "category": "화면 설정",
            "usageScenario": "정식 식사만 관리하고 싶을 때",
            "problemSolved": "간식까지 표시되어 식단이 복잡해 보임",
            "userBenefit": "식사 중심으로 깔끔한 기록 관리"
        }
    },

    "rapport-map": {
        "데이터를 마구 던지면 저장해주는 메모 기능": {
            "category": "빠른 기록",
            "usageScenario": "만남 직후 대화 내용을 바로 메모하고 싶을 때",
            "problemSolved": "시간 지나면 대화 내용을 잊어버림",
            "userBenefit": "30초 안에 핵심 내용 기록 완료"
        },
        "멘티들과 했던 행동들에 사진으로 기억할 수 있도록 돕기": {
            "category": "시각적 기록",
            "usageScenario": "멘토링 활동을 사진으로 남기고 싶을 때",
            "problemSolved": "텍스트만으로는 그 순간의 감정을 기억하기 어려움",
            "userBenefit": "사진으로 생생하게 추억 보존"
        },
        "기록에 태그를 남기고 태그로 필터링 해서 볼 수 있도록 하기": {
            "category": "검색과 정리",
            "usageScenario": "특정 주제로 나눴던 대화를 다시 찾고 싶을 때",
            "problemSolved": "많은 기록 중에서 원하는 내용 찾기 어려움",
            "userBenefit": "#커리어 #고민 등 태그로 즉시 검색"
        },
        "멘토링이나 어떤 특정 태그처럼 속성 중에 멘토링 케이스를 추가할 수 있었으면 좋겠음": {
            "category": "관계 유형 분류",
            "usageScenario": "멘토링, 친구, 동료 등 관계를 구분하고 싶을 때",
            "problemSolved": "모든 사람이 한 목록에 섞여 있음",
            "userBenefit": "관계 유형별로 분류하여 체계적 관리"
        },
        "위젯으로 다가오는 이벤트 볼 수 있게 해주기": {
            "category": "일정 알림",
            "usageScenario": "오늘 만날 사람을 아침에 확인하고 싶을 때",
            "problemSolved": "앱을 열어야만 일정을 확인 가능",
            "userBenefit": "홈 화면에서 오늘의 만남 즉시 확인"
        },
        "녹음 중 일때 좀 더 쉽게 다이나믹 아일랜드": {
            "category": "음성 기록",
            "usageScenario": "대화를 녹음 중일 때 상태를 확인하고 싶을 때",
            "problemSolved": "녹음 중임을 잊고 중요한 내용 놓침",
            "userBenefit": "항상 보이는 녹음 상태 표시"
        },
        "Core Spotlight - Spotlight 검색 으로 사람 쉽게 검색하기": {
            "category": "검색과 정리",
            "usageScenario": "특정 사람의 정보를 빠르게 찾고 싶을 때",
            "problemSolved": "앱을 열고 검색해야 하는 번거로움",
            "userBenefit": "시스템 검색에서 즉시 사람 찾기"
        },
        "만난 장소도 기록해주기": {
            "category": "맥락 기록",
            "usageScenario": "어디서 만났는지도 함께 기억하고 싶을 때",
            "problemSolved": "만난 장소를 기억하지 못함",
            "userBenefit": "장소와 함께 추억 회상"
        },
        "메모에서 자연스럽게 데이터를 추출해서 필요한 곳에 녹이기": {
            "category": "자동화",
            "usageScenario": "자유롭게 메모했는데 자동으로 정리되길 원할 때",
            "problemSolved": "정해진 양식에 맞춰 입력하는 번거로움",
            "userBenefit": "자연어 메모를 AI가 자동 구조화"
        },
        "클라우드 백업기능": {
            "category": "데이터 안전",
            "usageScenario": "기기를 잃어버렸을 때",
            "problemSolved": "소중한 관계 기록이 모두 사라짐",
            "userBenefit": "클라우드 백업으로 안전하게 보관"
        },
        "MessageUI - 빠른 연락": {
            "category": "빠른 연락",
            "usageScenario": "기록을 보다가 바로 연락하고 싶을 때",
            "problemSolved": "연락처 앱을 따로 열어야 함",
            "userBenefit": "한 번의 탭으로 전화/메시지 발송"
        },
        "Push Notifications + Background Tasks - 스마트 알림": {
            "category": "일정 알림",
            "usageScenario": "오랫동안 연락하지 않은 사람을 잊어버릴 때",
            "problemSolved": "소중한 관계를 방치하게 됨",
            "userBenefit": "일정 주기로 연락 제안"
        },
        "App Intents + Siri Shortcuts - 음성 명령": {
            "category": "빠른 기록",
            "usageScenario": "운전 중 만남을 기록하고 싶을 때",
            "problemSolved": "손을 쓸 수 없는 상황",
            "userBenefit": "시리로 음성 명령만으로 기록"
        },
        "음성 개선": {
            "category": "음성 기록",
            "usageScenario": "중요한 대화를 녹음해 두고 싶을 때",
            "problemSolved": "음질이 나빠서 나중에 듣기 어려움",
            "userBenefit": "선명한 음질로 대화 재생"
        },
        "멘토링 트래킹": {
            "category": "진행 추적",
            "usageScenario": "멘티의 성장 과정을 관리하고 싶을 때",
            "problemSolved": "몇 번 만났는지, 어떤 진전이 있었는지 모름",
            "userBenefit": "멘토링 회차와 성과 시각화"
        },
        "사람관계보기": {
            "category": "관계 분석",
            "usageScenario": "내 인맥이 어떻게 연결되어 있는지 궁금할 때",
            "problemSolved": "누가 누구를 소개해줬는지 기억 안 남",
            "userBenefit": "관계망 시각화로 네트워킹 파악"
        }
    },

    "donkko-mart": {
        "나의 마트 추가하는 경험 개선": {
            "category": "마트 등록",
            "usageScenario": "자주 가는 마트를 앱에 등록하고 싶을 때",
            "problemSolved": "마트 등록이 복잡하고 어려움",
            "userBenefit": "3탭 안에 마트 등록 완료"
        },
        "위젯 화면 개선": {
            "category": "빠른 확인",
            "usageScenario": "마트 가기 전에 살 것들을 확인하고 싶을 때",
            "problemSolved": "앱을 열어야만 목록 확인 가능",
            "userBenefit": "홈 화면에서 장보기 목록 즉시 확인"
        },
        "개발자 소통화면": {
            "category": "피드백",
            "usageScenario": "앱에 필요한 기능을 제안하고 싶을 때",
            "problemSolved": "개발자에게 연락할 방법이 없음",
            "userBenefit": "직접 피드백하여 원하는 기능 요청"
        }
    },

    "bucket-climb": {
        "기본 버킷리스트 CRUD": {
            "category": "목표 관리",
            "usageScenario": "꿈과 목표를 적고 완료 체크하고 싶을 때",
            "problemSolved": "머릿속 목표가 흩어져 있음",
            "userBenefit": "한 곳에 모든 꿈을 정리하고 달성 추적"
        },
        "사진 첨부 기능 (단일)": {
            "category": "시각화",
            "usageScenario": "목표를 사진으로 구체화하고 싶을 때",
            "problemSolved": "텍스트만으로는 동기부여가 약함",
            "userBenefit": "사진으로 꿈을 시각화하여 강한 동기부여"
        },
        "다중 사진 첨부 기능 구현": {
            "category": "과정 기록",
            "usageScenario": "목표 달성 과정을 사진으로 남기고 싶을 때",
            "problemSolved": "결과만 기록되고 과정은 남지 않음",
            "userBenefit": "여러 장의 사진으로 여정 스토리 완성"
        },
        "카테고리 시스템 개선": {
            "category": "분류와 정리",
            "usageScenario": "여행, 커리어, 취미 등 분야별로 목표를 나누고 싶을 때",
            "problemSolved": "모든 목표가 섞여서 복잡함",
            "userBenefit": "분야별 균형잡힌 목표 설정"
        },
        "앱 로딩 성능 최적화": {
            "category": "빠른 실행",
            "usageScenario": "아침에 앱을 열어 오늘의 목표를 확인할 때",
            "problemSolved": "앱 로딩이 느려서 답답함",
            "userBenefit": "1초 안에 앱 시작"
        },
        "위젯 랜덤 버킷리스트 표시": {
            "category": "동기부여",
            "usageScenario": "하루에 한 번씩 꿈을 상기하고 싶을 때",
            "problemSolved": "앱을 열지 않으면 목표를 잊음",
            "userBenefit": "홈 화면에서 랜덤 목표로 매일 자극"
        },
        "소셜 공유 기능": {
            "category": "공유하기",
            "usageScenario": "달성한 목표를 친구들에게 자랑하고 싶을 때",
            "problemSolved": "성취를 혼자만 알고 있음",
            "userBenefit": "SNS 공유로 축하받고 동기부여"
        },
        "통계 대시보드": {
            "category": "진행 추적",
            "usageScenario": "올해 얼마나 달성했는지 확인하고 싶을 때",
            "problemSolved": "전체적인 진행 상황을 파악하기 어려움",
            "userBenefit": "달성률, 카테고리별 분포 등 한눈에 확인"
        }
    },

    "bami-log": {
        "진통기록 + 호흡을 도와주는 것 추가": {
            "category": "출산 준비",
            "usageScenario": "진통이 시작되어 간격을 측정하고 호흡 조절이 필요할 때",
            "problemSolved": "진통 간격을 종이에 적거나 다른 앱을 찾느라 당황하는 상황",
            "userBenefit": "진통 시작부터 병원 가는 시점까지 정확한 기록과 호흡 가이드로 안심"
        },
        "학습 노트 작성": {
            "category": "빠른 기록",
            "usageScenario": "육아 강의나 독서 직후 중요 내용을 빠르게 메모하고 싶을 때",
            "problemSolved": "배운 내용을 나중에 적으려다 잊어버리는 문제",
            "userBenefit": "30초 안에 핵심만 기록하고 태그로 쉽게 찾기"
        },
        "복습 스케줄링": {
            "category": "학습 효율",
            "usageScenario": "배운 내용을 언제 다시 봐야 할지 모를 때",
            "problemSolved": "복습 타이밍을 놓쳐서 결국 잊어버리는 문제",
            "userBenefit": "과학적 복습 주기에 맞춰 자동 알림으로 장기 기억 형성"
        }
    },

    "cooltime": {
        "자동 타이머": {
            "category": "건강 알림",
            "usageScenario": "업무에 집중하다가 눈 쉬는 것을 잊을 때",
            "problemSolved": "장시간 화면 사용으로 눈이 피로하고 건조해지는 문제",
            "userBenefit": "20분마다 자동 알림으로 규칙적인 눈 휴식 습관 형성"
        },
        "눈 운동 가이드": {
            "category": "건강 관리",
            "usageScenario": "휴식 시간에 눈을 쉬면서 적극적인 운동을 하고 싶을 때",
            "problemSolved": "단순히 화면에서 눈을 떼는 것만으로는 피로 회복이 부족함",
            "userBenefit": "따라하기 쉬운 눈 운동으로 눈 건강 적극 개선"
        }
    },

    "daily-compliment": {
        "컨텐츠 추가": {
            "category": "콘텐츠 다양성",
            "usageScenario": "매일 같은 칭찬을 받아서 신선함이 떨어질 때",
            "problemSolved": "반복되는 메시지로 감동이 줄어드는 문제",
            "userBenefit": "매일 새로운 칭찬으로 지속적인 긍정 에너지 획득"
        },
        "일일 칭찬 메시지": {
            "category": "하루 시작",
            "usageScenario": "아침에 일어나서 긍정적인 마음으로 하루를 시작하고 싶을 때",
            "problemSolved": "부정적인 생각이나 불안으로 하루를 시작하는 문제",
            "userBenefit": "매일 아침 따뜻한 칭찬으로 자존감 향상과 긍정적 하루 시작"
        },
        "칭찬 모음집": {
            "category": "감정 회복",
            "usageScenario": "힘든 일이 있어서 위로가 필요할 때",
            "problemSolved": "현재 기분이 안 좋을 때 긍정적 메시지가 필요함",
            "userBenefit": "과거에 받았던 칭찬들을 다시 보며 자신감 회복"
        }
    },

    "double-reminder": {
        "이중 알림 설정": {
            "category": "확실한 알림",
            "usageScenario": "중요한 약속을 절대 놓치면 안 될 때",
            "problemSolved": "한 번의 알림을 놓쳐서 중요한 일정을 망치는 상황",
            "userBenefit": "두 번의 알림으로 안전장치 확보, 마음의 안정"
        },
        "유연한 간격 설정": {
            "category": "맞춤 설정",
            "usageScenario": "상황에 따라 다른 알림 간격이 필요할 때",
            "problemSolved": "고정된 간격으로는 다양한 상황에 대응하기 어려움",
            "userBenefit": "5분 전, 1시간 전 등 상황에 맞는 완벽한 알림 설정"
        },
        "UI 개선작업": {
            "category": "사용 편의성",
            "usageScenario": "알림 관리 화면이 복잡해서 헷갈릴 때",
            "problemSolved": "직관적이지 않은 UI로 설정이 어려움",
            "userBenefit": "한눈에 이해되는 화면으로 빠른 설정"
        },
        "예비알림 마크 개선": {
            "category": "시각적 구분",
            "usageScenario": "어떤 알림에 예비가 설정되어 있는지 확인하고 싶을 때",
            "problemSolved": "예비 알림 설정 여부를 확인하기 어려움",
            "userBenefit": "한눈에 예비 알림 설정 상태 파악"
        },
        "온보딩 개선": {
            "category": "첫 사용 지원",
            "usageScenario": "앱을 처음 설치하고 어떻게 쓰는지 모를 때",
            "problemSolved": "핵심 가치를 이해하지 못해 앱을 삭제함",
            "userBenefit": "이중 알림의 장점을 빠르게 이해하고 바로 활용"
        },
        "각각 알림마다 노티 레이블 넣기": {
            "category": "명확한 정보",
            "usageScenario": "알림을 받았을 때 이게 첫 번째인지 두 번째인지 궁금할 때",
            "problemSolved": "지금 받은 알림이 마지막인지 아닌지 알 수 없음",
            "userBenefit": "알림 순서를 바로 알아 적절한 행동 선택 가능"
        },
        "다음 알림까지 남은 시간 보여주기": {
            "category": "시간 관리",
            "usageScenario": "다음 알림이 언제 올지 예상하고 싶을 때",
            "problemSolved": "다음 알림 시간을 계산해야 하는 번거로움",
            "userBenefit": "남은 시간을 보고 여유롭게 준비"
        },
        "사용자가 사용했던 타이머의 기록 남기기와 빠른 타이머 그리고 그 레이블링": {
            "category": "빠른 설정",
            "usageScenario": "자주 쓰는 알림 패턴을 매번 설정하기 귀찮을 때",
            "problemSolved": "반복적으로 같은 시간을 입력하는 번거로움",
            "userBenefit": "자주 쓰는 패턴을 저장하여 한 번의 탭으로 설정"
        },
        "내가 기록한 정보 중 저장된 것 아이클라우드 동기화": {
            "category": "기기 간 연동",
            "usageScenario": "아이폰과 아이패드 모두에서 같은 알림을 받고 싶을 때",
            "problemSolved": "기기마다 알림을 따로 설정해야 하는 불편함",
            "userBenefit": "모든 기기에서 동일한 알림 자동 동기화"
        },
        "접근성 개선": {
            "category": "모두를 위한 접근성",
            "usageScenario": "시각 장애가 있거나 큰 글씨가 필요할 때",
            "problemSolved": "기본 설정으로는 사용하기 어려움",
            "userBenefit": "VoiceOver, 큰 글씨 지원으로 누구나 사용 가능"
        },
        "권한 거부 되었을 때 다시 하는 법 혹은 부작용 안내": {
            "category": "문제 해결 지원",
            "usageScenario": "알림 권한을 거부했더니 앱이 작동하지 않을 때",
            "problemSolved": "권한 문제로 앱을 못 쓰고 포기하는 상황",
            "userBenefit": "친절한 가이드로 쉽게 권한 설정 완료"
        },
        "사용자 사운드 커스터마이징": {
            "category": "개인화",
            "usageScenario": "기본 알림음이 마음에 들지 않을 때",
            "problemSolved": "획일적인 알림음으로 거부감이 생김",
            "userBenefit": "좋아하는 소리로 알림을 받아 더 쾌적한 경험"
        },
        "다국어 지원 (영어 + 아시아 중심 - 일본, 중국)": {
            "category": "글로벌 지원",
            "usageScenario": "한국어가 아닌 다른 언어로 앱을 사용하고 싶을 때",
            "problemSolved": "한국어만 지원하여 외국인은 사용 불가",
            "userBenefit": "모국어로 편하게 앱 사용"
        }
    },

    "ecdesigner": {
        "명함 템플릿": {
            "category": "빠른 시작",
            "usageScenario": "명함 디자인을 처음 해봐서 어떻게 시작할지 모를 때",
            "problemSolved": "빈 캔버스 앞에서 막막함",
            "userBenefit": "전문 디자인 템플릿으로 5분 안에 명함 완성"
        },
        "드래그 앤 드롭 편집": {
            "category": "직관적 편집",
            "usageScenario": "텍스트와 로고 위치를 조정하고 싶을 때",
            "problemSolved": "복잡한 디자인 도구로 인한 학습 장벽",
            "userBenefit": "마우스로 드래그만 하면 자유롭게 배치"
        },
        "흰 배경 + 스냅그리드": {
            "category": "정렬 지원",
            "usageScenario": "요소들을 정확하게 정렬하고 싶을 때",
            "problemSolved": "손으로 정렬하면 미세하게 어긋남",
            "userBenefit": "자동 스냅으로 픽셀 단위 정렬 완성"
        },
        "사이드바-캔버스 분리": {
            "category": "작업 공간 확보",
            "usageScenario": "명함을 더 크게 보면서 작업하고 싶을 때",
            "problemSolved": "도구가 화면을 차지해서 캔버스가 작음",
            "userBenefit": "넓은 작업 공간으로 편안한 디자인"
        },
        "헤더 아이콘 정리 (엘립시스 메뉴)": {
            "category": "깔끔한 UI",
            "usageScenario": "자주 쓰지 않는 기능들이 화면을 어지럽힐 때",
            "problemSolved": "너무 많은 버튼으로 인한 혼란",
            "userBenefit": "핵심 기능만 보여서 집중력 향상"
        },
        "사이드바 단순화 (우클릭 메뉴)": {
            "category": "빠른 작업",
            "usageScenario": "편집 작업을 더 빠르게 하고 싶을 때",
            "problemSolved": "메뉴를 찾아 클릭하는 시간 낭비",
            "userBenefit": "우클릭으로 즉시 원하는 기능 실행"
        },
        "Tips 영역 하단 분리": {
            "category": "학습 지원",
            "usageScenario": "기능 사용법이 궁금하지만 화면을 가리면 안 될 때",
            "problemSolved": "도움말이 작업 화면을 방해함",
            "userBenefit": "필요할 때만 팁을 펼쳐서 확인"
        },
        "마일스톤 > EC 계층 구조": {
            "category": "체계적 관리",
            "usageScenario": "복잡한 프로젝트를 단계별로 관리하고 싶을 때",
            "problemSolved": "모든 작업이 섞여서 진행 상황 파악 어려움",
            "userBenefit": "단계별로 나누어 체계적인 프로젝트 진행"
        }
    },

    "life-restaurant": {
        "맛집 기록": {
            "category": "추억 저장",
            "usageScenario": "맛있게 먹은 식당을 나중에도 기억하고 싶을 때",
            "problemSolved": "시간이 지나면 어디가 맛있었는지 잊어버림",
            "userBenefit": "사진, 메모, 평점으로 생생하게 기록"
        },
        "맛집 지도": {
            "category": "위치 기반 검색",
            "usageScenario": "지금 있는 곳 근처에 내가 가본 맛집이 있는지 확인하고 싶을 때",
            "problemSolved": "근처에 좋은 곳이 있어도 기억이 안 남",
            "userBenefit": "지도에서 한눈에 주변 맛집 확인"
        },
        "방문 횟수": {
            "category": "단골 파악",
            "usageScenario": "어떤 식당을 가장 자주 가는지 궁금할 때",
            "problemSolved": "단골집인지 아닌지 기억이 애매함",
            "userBenefit": "자동 카운트로 진짜 단골집 파악"
        },
        "진짜 맛 있다는 것은": {
            "category": "특별 표시",
            "usageScenario": "별점과 별개로 정말 추천하고 싶은 곳을 강조하고 싶을 때",
            "problemSolved": "별점만으로는 진짜 맛집을 구분하기 어려움",
            "userBenefit": "특별한 마크로 최애 맛집 표시"
        },
        "사람들 추가하기": {
            "category": "추억 강화",
            "usageScenario": "누구랑 갔는지도 함께 기록하고 싶을 때",
            "problemSolved": "맛집 정보만 있고 누구와 갔는지는 모름",
            "userBenefit": "함께한 사람 기록으로 더 풍부한 추억"
        },
        "검색은 카카오 API": {
            "category": "빠른 등록",
            "usageScenario": "식당 정보를 일일이 입력하기 귀찮을 때",
            "problemSolved": "주소, 전화번호 등을 수동으로 입력하는 번거로움",
            "userBenefit": "식당 이름만 검색하면 정보 자동 입력"
        },
        "특정 위치에 들어가면 알림을 주는 것": {
            "category": "위치 알림",
            "usageScenario": "근처에 가보려던 맛집이 있는데 까먹을 때",
            "problemSolved": "근처에 왔는데도 맛집을 떠올리지 못함",
            "userBenefit": "근처 접근 시 자동 알림으로 방문 유도"
        },
        "도형 은 절반으로 보여야지": {
            "category": "세밀한 평가",
            "usageScenario": "3점과 4점 사이의 미묘한 평가를 하고 싶을 때",
            "problemSolved": "정수 별점으로는 세밀한 평가 불가",
            "userBenefit": "반쪽 별점으로 더 정확한 평가"
        },
        "친구에게 리스트 공유할 수 있게하기": {
            "category": "공유하기",
            "usageScenario": "친구에게 맛집 리스트를 추천하고 싶을 때",
            "problemSolved": "일일이 메시지로 보내야 하는 번거로움",
            "userBenefit": "한 번에 맛집 리스트 공유"
        }
    },

    "pixel-mimi": {
        "픽셀 캔버스": {
            "category": "자유로운 창작",
            "usageScenario": "간단한 픽셀 아트를 그리고 싶을 때",
            "problemSolved": "복잡한 그래픽 툴은 배우기 어려움",
            "userBenefit": "직관적인 그리드에서 쉽게 픽셀 아트 제작"
        },
        "색상 팔레트": {
            "category": "일관된 스타일",
            "usageScenario": "자주 쓰는 색을 매번 찾기 귀찮을 때",
            "problemSolved": "같은 색을 다시 찾느라 시간 낭비",
            "userBenefit": "색상 저장으로 일관된 색조의 작품 완성"
        },
        "이걸 돈 받으려면 뭘 제공할지 고민하기": {
            "category": "기타",
            "usageScenario": "프리미엄 기능을 고민 중일 때",
            "problemSolved": "무료 앱의 수익 모델 부재",
            "userBenefit": "향후 프리미엄 기능 제공 가능성"
        }
    },

    "probability-calculator": {
        "확률 계산기": {
            "category": "복잡한 계산",
            "usageScenario": "조합이나 순열 문제를 풀어야 하는데 계산이 복잡할 때",
            "problemSolved": "수식을 외우지 못하거나 계산 실수",
            "userBenefit": "숫자만 입력하면 정확한 확률 계산"
        },
        "시각화 그래프": {
            "category": "직관적 이해",
            "usageScenario": "확률을 숫자로만 보면 감이 안 올 때",
            "problemSolved": "추상적인 확률을 이해하기 어려움",
            "userBenefit": "그래프로 확률을 시각적으로 이해"
        }
    },

    "quiz": {
        "퀴즈 플레이": {
            "category": "재미있는 학습",
            "usageScenario": "지루하지 않게 지식을 테스트하고 싶을 때",
            "problemSolved": "단순 암기는 재미없고 지속하기 어려움",
            "userBenefit": "게임처럼 즐기며 새로운 지식 습득"
        },
        "퀴즈 생성": {
            "category": "콘텐츠 제작",
            "usageScenario": "내가 아는 지식을 퀴즈로 만들어 공유하고 싶을 때",
            "problemSolved": "퀴즈 제작 도구가 복잡하거나 없음",
            "userBenefit": "쉬운 에디터로 나만의 퀴즈 제작"
        },
        "캐싱으로 문제 저장 및 API 최소화": {
            "category": "오프라인 지원",
            "usageScenario": "인터넷이 없는 곳에서도 퀴즈를 풀고 싶을 때",
            "problemSolved": "네트워크 없이는 앱 사용 불가",
            "userBenefit": "한 번 받은 퀴즈는 오프라인에서도 가능"
        }
    },

    "rainbow-of-desire": {
        "감정 색상 기록": {
            "category": "감정 표현",
            "usageScenario": "복잡한 감정을 말로 표현하기 어려울 때",
            "problemSolved": "감정을 글로 쓰기 부담스러움",
            "userBenefit": "색깔 선택만으로 간단하게 감정 기록"
        },
        "감정 캘린더": {
            "category": "패턴 파악",
            "usageScenario": "한 달간 나의 감정 변화를 한눈에 보고 싶을 때",
            "problemSolved": "전체적인 감정 흐름을 파악하기 어려움",
            "userBenefit": "색상 캘린더로 감정 패턴 시각화"
        },
        "특정 날짜만 제외하는 기능": {
            "category": "유연한 추적",
            "usageScenario": "휴가나 특별한 날은 기록에서 제외하고 싶을 때",
            "problemSolved": "완벽주의 압박으로 습관 포기",
            "userBenefit": "예외일 설정으로 부담 없는 기록"
        },
        "클라우드 킷 적용해서 데이터 동기화": {
            "category": "기기 간 연동",
            "usageScenario": "아이폰에서 기록한 감정을 아이패드에서도 보고 싶을 때",
            "problemSolved": "기기를 바꾸면 기록이 사라짐",
            "userBenefit": "모든 기기에서 감정 기록 동기화"
        },
        "일정관리 리스트로 하기": {
            "category": "체계적 관리",
            "usageScenario": "감정을 일정처럼 관리하고 싶을 때",
            "problemSolved": "산발적인 기록으로 관리가 어려움",
            "userBenefit": "리스트 뷰로 체계적인 감정 추적"
        },
        "캘린더를 불러오는 실험": {
            "category": "맥락 이해",
            "usageScenario": "어떤 일정이 나를 힘들게 했는지 알고 싶을 때",
            "problemSolved": "감정과 일정의 연결고리를 모름",
            "userBenefit": "일정과 감정을 함께 보며 원인 파악"
        },
        "일정 패턴 다양하게 시각화 필요": {
            "category": "다각도 분석",
            "usageScenario": "여러 방식으로 감정 데이터를 분석하고 싶을 때",
            "problemSolved": "한 가지 차트로는 인사이트 부족",
            "userBenefit": "다양한 차트로 깊이 있는 감정 분석"
        },
        "매일 계속되는 것, 시작점과 끝점이 없는것 만들기": {
            "category": "지속 상태 기록",
            "usageScenario": "특정 시간이 아닌 하루 종일 지속되는 기분을 기록할 때",
            "problemSolved": "순간적 감정만 기록 가능",
            "userBenefit": "연속적인 감정 상태 표현 가능"
        }
    },

    "rebound-journal": {
        "회복 일지": {
            "category": "회복 기록",
            "usageScenario": "힘든 시기를 극복하는 과정을 기록하고 싶을 때",
            "problemSolved": "작은 진전을 알아차리지 못함",
            "userBenefit": "매일의 긍정적 변화를 기록하며 희망 유지"
        },
        "회복 그래프": {
            "category": "진행 추적",
            "usageScenario": "전체적으로 나아지고 있는지 확인하고 싶을 때",
            "problemSolved": "주관적으로는 변화를 느끼기 어려움",
            "userBenefit": "그래프로 회복 추세를 객관적으로 확인"
        }
    },

    "relax-on": {
        "자연 소리 재생": {
            "category": "힐링 사운드",
            "usageScenario": "스트레스를 해소하거나 집중하고 싶을 때",
            "problemSolved": "조용한 공간이 없거나 소음이 방해됨",
            "userBenefit": "비, 파도 소리로 편안함과 집중력 향상"
        },
        "소리 믹싱": {
            "category": "맞춤 힐링",
            "usageScenario": "여러 소리를 섞어서 나만의 완벽한 환경을 만들고 싶을 때",
            "problemSolved": "단일 소리만으로는 만족도가 낮음",
            "userBenefit": "비+천둥, 파도+새소리 등 조합으로 최적 사운드 제작"
        }
    },

    "schedule-assistant": {
        "스마트 일정 추천": {
            "category": "AI 추천",
            "usageScenario": "할 일은 많은데 언제 무엇을 해야 할지 모를 때",
            "problemSolved": "일정 계획 세우는 데만 시간 낭비",
            "userBenefit": "AI가 최적 시간대를 제안해서 바로 실행"
        },
        "캘린더 통합": {
            "category": "통합 관리",
            "usageScenario": "여러 캘린더 앱을 오가며 확인하는 것이 불편할 때",
            "problemSolved": "캘린더가 분산되어 전체 일정 파악 어려움",
            "userBenefit": "한 곳에서 모든 캘린더 통합 관리"
        },
        "너 이거 다 했어? 라고 물어봐주기": {
            "category": "친근한 리마인더",
            "usageScenario": "해야 할 일을 잊고 있을 때",
            "problemSolved": "차가운 알림은 부담스럽고 무시하게 됨",
            "userBenefit": "친근한 톤의 알림으로 부담 없이 상기"
        }
    },

    "shared-day-designer": {
        "공유 캘린더": {
            "category": "가족 협업",
            "usageScenario": "가족끼리 서로의 일정을 확인하고 조율하고 싶을 때",
            "problemSolved": "각자 일정을 따로 관리해서 겹치는 문제 발생",
            "userBenefit": "실시간으로 가족 일정 공유하여 충돌 방지"
        },
        "일정 알림": {
            "category": "공동 알림",
            "usageScenario": "가족 행사를 모두가 기억해야 할 때",
            "problemSolved": "한 명만 기억하고 다른 사람은 잊어버림",
            "userBenefit": "모든 구성원이 동시에 알림 받아 함께 준비"
        }
    }
}

# 다른 앱들도 계속 추가...
# 이 패턴을 모든 앱에 적용


def load_app_json(app_file):
    """앱 JSON 파일 로드"""
    with open(app_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_app_json(app_file, data):
    """앱 JSON 파일 저장"""
    with open(app_file, 'r', encoding='utf-8') as f:
        original = f.read()

    # 백업
    backup_file = app_file.with_suffix('.json.backup5')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original)

    # 저장
    with open(app_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def recategorize_features(app_file):
    """feature 카테고리 재분류"""
    app_id = app_file.stem
    data = load_app_json(app_file)

    if app_id not in FEATURE_RECATEGORIZATION:
        print(f"⚠ {data.get('name', app_id)}: 재분류 데이터 없음")
        return 0

    recategorization_map = FEATURE_RECATEGORIZATION[app_id]
    updated_count = 0

    for task in data.get('allTasks', []):
        task_name = task['name']

        # feature인지 확인
        if 'featureMetadata' not in task or not task['featureMetadata']:
            continue

        # 재분류 정보가 있는 경우
        if task_name in recategorization_map:
            new_info = recategorization_map[task_name]

            # 기존 메타데이터 유지하면서 업데이트
            task['featureMetadata']['category'] = new_info['category']

            # 새로운 필드 추가
            task['featureMetadata']['usageScenario'] = new_info['usageScenario']
            task['featureMetadata']['problemSolved'] = new_info['problemSolved']
            task['featureMetadata']['userBenefit'] = new_info['userBenefit']

            updated_count += 1

    if updated_count > 0:
        save_app_json(app_file, data)
        print(f"✅ {data.get('name', app_id)}: {updated_count}개 feature 재분류")
        return updated_count
    else:
        return 0


def main():
    """메인 실행"""
    print("=" * 80)
    print("Feature 카테고리 재분류 - 20년차 기획자 관점")
    print("=" * 80)
    print()

    app_files = sorted(APPS_DIR.glob("*.json"))
    total_updated = 0

    for app_file in app_files:
        count = recategorize_features(app_file)
        total_updated += count

    print()
    print("=" * 80)
    print(f"총 {total_updated}개 feature 재분류 완료")
    print()
    print("추가된 정보:")
    print("  - usageScenario: 언제 이 기능을 사용하는가")
    print("  - problemSolved: 어떤 문제를 해결하는가")
    print("  - userBenefit: 사용자가 얻는 구체적 이득")
    print("=" * 80)


if __name__ == "__main__":
    main()

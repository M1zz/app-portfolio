#!/usr/bin/env python3
"""
각 앱의 포텐셜과 가능성 분석 추가
20년차 기획자 관점에서 시장 기회, 성장 가능성, 수익화 전략 등을 정의
"""

import json
from pathlib import Path

APPS_DIR = Path("/Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO/Data/apps")

# 각 앱별 포텐셜 분석
APP_POTENTIALS = {
    "clip-keyboard": {
        "marketSize": "생산성 앱 시장 - 글로벌 수억 명의 지식 근로자",
        "targetExpansion": [
            "개인 사용자 → 기업 구독 모델",
            "한국 → 글로벌 (영어, 일본어, 중국어)",
            "개발자 → 모든 반복 업무 종사자 (세일즈, CS, 마케터)"
        ],
        "monetization": {
            "current": "무료/유료",
            "potential": [
                "프리미엄 구독 (월 $4.99): 무제한 템플릿, 통계, 팀 동기화",
                "기업용 라이선스 (사용자당 $2.99/월): 팀 템플릿 공유, 관리자 대시보드",
                "API 제공: 다른 앱에서 템플릿 사용"
            ]
        },
        "competitiveAdvantage": [
            "시간 절약을 숫자로 시각화 - 경쟁사에 없는 독특한 기능",
            "iOS 네이티브 키보드 익스텐션 - 모든 앱에서 사용 가능",
            "한국 시장 1위 확보 후 글로벌 확장 전략"
        ],
        "expansionStrategy": [
            "1단계: macOS/iPadOS 완벽 지원으로 애플 생태계 장악",
            "2단계: 팀 기능 추가로 B2B 시장 진출",
            "3단계: AI 기반 자동 템플릿 생성 및 추천",
            "4단계: 음성-텍스트 템플릿 변환으로 접근성 확대"
        ],
        "longTermVision": "전 세계 지식 근로자의 필수 생산성 도구. '텍스트 반복 = 클립키보드'라는 브랜드 확립. 5년 내 MAU 100만 달성.",
        "risks": [
            "iOS 키보드 정책 변경 위험",
            "ChatGPT 등 AI 도구와의 경쟁"
        ],
        "opportunities": [
            "재택근무 확대로 생산성 도구 수요 증가",
            "AI와 결합하여 맥락 기반 템플릿 자동 추천"
        ]
    },

    "three-meals": {
        "marketSize": "건강/다이어트 앱 시장 - 한국만 1000만+ 잠재 사용자",
        "targetExpansion": [
            "다이어트 관심층 → 만성질환 관리 (당뇨, 고혈압)",
            "개인 사용자 → 영양사-고객 연결 플랫폼",
            "한국 → 아시아 (식단 문화가 유사한 일본, 중국)"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 $9.99): AI 영양사, 맞춤 식단 추천, 상세 분석",
                "영양사 연결 서비스 (건당 $29.99): 전문가 1:1 상담",
                "식품 브랜드 제휴: 건강 식품 추천 커미션"
            ]
        },
        "competitiveAdvantage": [
            "사진 기반 자동 식단 분석 - 입력 부담 최소화",
            "AI 영양소 추출 정확도",
            "긍정적 피드백 중심 - 스트레스 없는 건강 관리"
        ],
        "expansionStrategy": [
            "1단계: AI 정확도 개선 (95% 이상 영양소 인식률)",
            "2단계: 커뮤니티 기능 추가 - 식단 공유 및 동기부여",
            "3단계: 웨어러블 연동 (Apple Watch) - 운동과 식단 통합 관리",
            "4단계: 영양사 마켓플레이스 오픈"
        ],
        "longTermVision": "아시아 1위 AI 영양 관리 플랫폼. 병원-환자 연결로 만성질환 관리 솔루션 제공. 3년 내 MAU 50만 달성.",
        "risks": [
            "AI 분석 오류로 인한 신뢰도 하락",
            "의료 영역 진입 시 규제 이슈"
        ],
        "opportunities": [
            "고령화 사회에서 건강 관리 수요 폭발적 증가",
            "보험사와 제휴하여 건강 리워드 프로그램 가능"
        ]
    },

    "rapport-map": {
        "marketSize": "CRM/네트워킹 시장 - 전문직, 프리랜서, 멘토 수백만 명",
        "targetExpansion": [
            "멘토링 → 세일즈, 컨설팅, 코칭 전문가",
            "개인 → 소규모 비즈니스 (10인 이하 스타트업)",
            "한국 → 글로벌 (영어권 멘토링 시장)"
        ],
        "monetization": {
            "current": "무료/유료",
            "potential": [
                "프리미엄 구독 (월 $7.99): 무제한 연락처, 음성 녹음, 고급 분석",
                "프로 버전 (월 $19.99): 팀 공유, CRM 연동, AI 인사이트",
                "멘토링 마켓플레이스: 멘토-멘티 매칭 수수료 (15%)"
            ]
        },
        "competitiveAdvantage": [
            "단순 연락처가 아닌 관계의 '맥락' 기록",
            "음성 녹음 + 자동 전사 + AI 요약",
            "멘토링 특화 기능 (세션 트래킹, 성장 기록)"
        ],
        "expansionStrategy": [
            "1단계: AI 기반 자동 메모 정리 및 인사이트 추출",
            "2단계: LinkedIn, 명함 OCR 연동으로 네트워킹 자동화",
            "3단계: 멘토-멘티 매칭 플랫폼으로 확장",
            "4단계: Slack/Notion 등 협업 툴 연동으로 B2B 진출"
        ],
        "longTermVision": "전문가들의 필수 관계 관리 도구. '인맥 관리 = 라포맵'이라는 브랜드. 멘토링 플랫폼으로 확장하여 교육 시장 진출.",
        "risks": [
            "프라이버시 우려 (녹음, 개인정보)",
            "대기업 CRM 툴과의 경쟁"
        ],
        "opportunities": [
            "긱 이코노미 확대로 개인 네트워킹 중요성 증가",
            "AI 기술 발전으로 관계 인사이트 자동 생성 가능"
        ]
    },

    "donkko-mart": {
        "marketSize": "장보기/가계부 앱 - 한국 전체 가구 2000만+",
        "targetExpansion": [
            "주부 → 1인 가구, 맞벌이 부부",
            "장보기 → 가계부 + 식재료 관리 통합 솔루션",
            "오프라인 → 온라인 마트 자동 주문 연동"
        ],
        "monetization": {
            "current": "유료 (₩4,400)",
            "potential": [
                "기본 무료 + 프리미엄 (월 ₩4,900): 마트 가격 비교, 할인 정보",
                "마트 제휴: 쿠폰 제공 및 커미션",
                "광고 모델: 타겟팅 식품 광고 (opt-in)"
            ]
        },
        "competitiveAdvantage": [
            "마트별 맞춤 리스트 - 경쟁사는 통합 리스트만 제공",
            "위젯으로 앱 열지 않고 확인 - 편의성 극대화",
            "가족 공유 기능 - 실시간 협업"
        ],
        "expansionStrategy": [
            "1단계: AI 기반 장보기 추천 (냉장고 재료 기반)",
            "2단계: 마트 가격 비교 및 최저가 알림",
            "3단계: 온라인 마트 API 연동 - 원클릭 주문",
            "4단계: 레시피 연동 - 필요한 재료 자동 추가"
        ],
        "longTermVision": "스마트 장보기의 표준. 오프라인-온라인 마트 통합 허브. 식재료 구매 데이터 기반 맞춤형 서비스 제공.",
        "risks": [
            "쿠팡, 마켓컬리 등 대형 플랫폼의 기능 통합",
            "마트별 제휴 없이는 차별화 어려움"
        ],
        "opportunities": [
            "식재료 가격 인플레이션으로 절약 니즈 증가",
            "온라인 장보기 습관화로 통합 관리 수요 상승"
        ]
    },

    "bucket-climb": {
        "marketSize": "자기계발/목표관리 시장 - 글로벌 수억 명",
        "targetExpansion": [
            "20-30대 → 전 연령층 (은퇴자의 버킷리스트)",
            "개인 → 커플, 가족 공유 버킷리스트",
            "목표 달성 → 경험 공유 커뮤니티"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 $3.99): 무제한 사진, 목표 분석, 프라이빗",
                "경험 마켓플레이스: 버킷리스트 달성 가이드 판매 (수수료 20%)",
                "여행사/액티비티 제휴: 예약 커미션"
            ]
        },
        "competitiveAdvantage": [
            "사진 중심 시각화 - Instagram의 감성 + 목표 관리",
            "과정 기록 - 결과만이 아닌 여정의 스토리",
            "동기부여 위젯 - 매일 꿈을 상기시킴"
        ],
        "expansionStrategy": [
            "1단계: 커뮤니티 기능 - 버킷리스트 공유 및 영감",
            "2단계: AI 추천 - 취향 기반 버킷리스트 제안",
            "3단계: 경험 가이드 마켓플레이스",
            "4단계: 여행/액티비티 예약 통합 플랫폼"
        ],
        "longTermVision": "꿈을 이루는 플랫폼. 버킷리스트를 단순 체크리스트가 아닌 인생 여정의 스토리북으로. 경험 공유 커뮤니티로 성장.",
        "risks": [
            "단순 목표 관리는 경쟁 앱 많음",
            "지속 사용률 유지 어려움"
        ],
        "opportunities": [
            "MZ세대의 경험 중시 트렌드",
            "소셜 미디어 연동으로 바이럴 가능성"
        ]
    },

    "cooltime": {
        "marketSize": "눈 건강/웰빙 앱 - 전 세계 PC 사용자 20억+ 명",
        "targetExpansion": [
            "개발자/디자이너 → 모든 사무직 근로자",
            "개인 → 기업 복지 프로그램",
            "눈 건강 → 종합 디지털 웰빙 (자세, 스트레칭)"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 $2.99): 고급 통계, 맞춤 프로그램, 광고 제거",
                "기업 라이선스 (직원당 $1/월): 팀 대시보드, 건강 리포트",
                "보험사 제휴: 눈 건강 관리 리워드 프로그램"
            ]
        },
        "competitiveAdvantage": [
            "과학적 근거 (20-20-20 규칙) 기반",
            "게이미피케이션 - 배지, 스트릭으로 습관 형성",
            "팀 챌린지 - 동료와 함께 건강 관리"
        ],
        "expansionStrategy": [
            "1단계: Windows/Android 버전 출시로 시장 확대",
            "2단계: 기업 복지 패키지로 B2B 진출",
            "3단계: 안과 의사 협력 - 눈 건강 전문 콘텐츠",
            "4단계: 종합 디지털 웰빙 플랫폼 (자세, 수면 등)"
        ],
        "longTermVision": "전 세계 사무직 근로자의 필수 건강 도구. 기업 복지 프로그램 표준. VDT 증후군 예방의 대명사.",
        "risks": [
            "무료 타이머 앱과의 경쟁",
            "기업 도입 없이는 성장 한계"
        ],
        "opportunities": [
            "재택근무로 장시간 화면 노출 증가",
            "기업의 직원 건강 관리 중요성 증대"
        ]
    },

    "daily-compliment": {
        "marketSize": "정신 건강/웰빙 앱 - 글로벌 수억 명",
        "targetExpansion": [
            "우울감 있는 사람 → 전체 인구 (일상 긍정 에너지)",
            "개인 → 기업 웰빙 프로그램",
            "한국 → 글로벌 (다국어 칭찬 콘텐츠)"
        ],
        "monetization": {
            "current": "유료 (₩4,400)",
            "potential": [
                "구독 모델 (월 ₩2,900): 매일 새로운 칭찬, 음성 메시지",
                "맞춤형 칭찬 (AI 생성): 사용자 맥락 반영",
                "기업 라이선스: 직원 동기부여 프로그램"
            ]
        },
        "competitiveAdvantage": [
            "한국어 특화 칭찬 멘트 - 문화적 맥락 반영",
            "부담 없는 긍정 - 강요하지 않는 따뜻함",
            "누적 칭찬 모음집 - 힘든 날의 위로"
        ],
        "expansionStrategy": [
            "1단계: AI 기반 개인화 칭찬 생성",
            "2단계: 음성/동영상 칭찬으로 콘텐츠 확장",
            "3단계: 커뮤니티 - 사용자 간 칭찬 주고받기",
            "4단계: 기업 웰빙 프로그램 진출"
        ],
        "longTermVision": "매일 아침 긍정 에너지의 원천. 정신 건강 관리의 첫걸음. 칭찬 문화 확산의 리더.",
        "risks": [
            "무료 명언 앱과의 경쟁",
            "반복 사용 시 식상함"
        ],
        "opportunities": [
            "정신 건강 인식 증가",
            "기업의 직원 웰빙 투자 확대"
        ]
    },

    "double-reminder": {
        "marketSize": "생산성/알람 앱 - 스마트폰 사용자 전체",
        "targetExpansion": [
            "건망증 있는 사람 → 모든 바쁜 직장인",
            "개인 일정 → 팀 프로젝트 데드라인 관리",
            "한국 → 글로벌 (시차 관리 기능 추가)"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 ₩3,900): 무제한 알림, 위치 기반, 고급 패턴",
                "기업 버전: 팀 프로젝트 데드라인 공유",
                "Siri Shortcuts 프리미엄 기능"
            ]
        },
        "competitiveAdvantage": [
            "이중 안전망 - 절대 놓치지 않는 신뢰",
            "유연한 간격 설정 - 상황별 최적화",
            "친근한 UX - 알림이 스트레스가 아님"
        ],
        "expansionStrategy": [
            "1단계: AI 학습 - 사용자 패턴 분석하여 최적 간격 제안",
            "2단계: 캘린더 연동 - 중요 일정 자동 이중 알림",
            "3단계: 팀 기능 - 프로젝트 마감 공유 알림",
            "4단계: 웨어러블 통합 - Apple Watch 햅틱"
        ],
        "longTermVision": "중요한 순간을 절대 놓치지 않는 안전망. 신뢰할 수 있는 알림의 표준. ADHD, 치매 환자를 위한 필수 도구.",
        "risks": [
            "기본 알림 앱으로도 충분하다는 인식",
            "너무 많은 알림으로 인한 피로"
        ],
        "opportunities": [
            "고령화 사회에서 기억 보조 도구 수요",
            "ADHD 인식 증가로 특화 도구 필요"
        ]
    },

    "ecdesigner": {
        "marketSize": "디자인/명함 제작 - 소상공인, 프리랜서 수백만 명",
        "targetExpansion": [
            "명함 → 로고, 전단지, SNS 썸네일 등 종합 디자인",
            "개인 → 소규모 비즈니스 (5인 이하)",
            "한국 → 글로벌 (다국어 템플릿)"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 템플릿 (개당 $2.99): 프리미엄 디자인",
                "구독 모델 (월 $9.99): 무제한 템플릿, AI 디자인",
                "인쇄 서비스 연동: 주문 커미션 20%"
            ]
        },
        "competitiveAdvantage": [
            "5분 안에 전문 명함 완성 - 극도의 간편함",
            "템플릿 품질 - 실제 디자이너 제작",
            "모바일 최적화 - 언제 어디서나 편집"
        ],
        "expansionStrategy": [
            "1단계: AI 디자인 생성 - 텍스트 입력만으로 자동 디자인",
            "2단계: 로고, 전단지, 포스터 등으로 확장",
            "3단계: 인쇄소 직접 연동 - 원클릭 주문",
            "4단계: 디자인 마켓플레이스 - 디자이너 수익 창출"
        ],
        "longTermVision": "모바일 디자인 도구의 새로운 표준. 디자인 지식 없이도 전문가 수준 결과물. 소상공인의 필수 도구.",
        "risks": [
            "Canva 같은 대형 플랫폼과의 경쟁",
            "무료 디자인 툴 넘쳐남"
        ],
        "opportunities": [
            "1인 사업자, 긱 워커 증가",
            "AI 디자인 기술 발전"
        ]
    },

    "life-restaurant": {
        "marketSize": "맛집/외식 시장 - 외식 인구 전체",
        "targetExpansion": [
            "개인 기록 → 소셜 맛집 공유 플랫폼",
            "맛집 기록 → 음식 사진 SNS",
            "한국 → 아시아 (외식 문화 활발)"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 ₩4,900): 무제한 사진, 고급 필터, 프라이빗",
                "레스토랑 제휴: 할인 쿠폰 및 예약 커미션",
                "맛집 가이드북 제작: 큐레이션 콘텐츠 판매"
            ]
        },
        "competitiveAdvantage": [
            "개인 평가 중심 - 대중 평점에 휘둘리지 않음",
            "사진 중심 - 시각적 기억",
            "위치 기반 빠른 검색"
        ],
        "expansionStrategy": [
            "1단계: 친구 팔로우 - 맛집 취향 공유",
            "2단계: AI 추천 - 내 입맛 기반 새 맛집 발견",
            "3단계: 레스토랑 예약 통합",
            "4단계: 맛집 인플루언서 플랫폼"
        ],
        "longTermVision": "개인화된 맛집 발견 플랫폼. 대중 평점이 아닌 내 취향 기반 추천. 미식가 커뮤니티의 허브.",
        "risks": [
            "네이버, 카카오 등 대형 플랫폼 독점",
            "개인 기록만으로는 성장 한계"
        ],
        "opportunities": [
            "외식 지출 증가 트렌드",
            "미식가 문화 확산"
        ]
    },

    "pixel-mimi": {
        "marketSize": "창작/취미 앱 - 픽셀 아트 애호가 글로벌 수백만",
        "targetExpansion": [
            "취미 → NFT 크리에이터",
            "개인 → 게임 개발자 (에셋 제작)",
            "픽셀 아트 → 도트 애니메이션"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 $4.99): 고급 도구, 레이어, 클라우드 저장",
                "NFT 민팅 연동: 작품 NFT 변환 수수료",
                "에셋 마켓플레이스: 게임 개발자에게 판매"
            ]
        },
        "competitiveAdvantage": [
            "모바일 최적화 - 언제 어디서나 창작",
            "직관적 UI - 배우기 쉬움",
            "소셜 공유 - 작품 쉽게 공유"
        ],
        "expansionStrategy": [
            "1단계: 애니메이션 기능 추가 - 움직이는 픽셀 아트",
            "2단계: 커뮤니티 - 작품 공유 및 챌린지",
            "3단계: NFT 연동 - 작품을 자산으로",
            "4단계: 게임 에셋 마켓플레이스"
        ],
        "longTermVision": "모바일 픽셀 아트의 표준. 취미 크리에이터가 수익을 창출하는 플랫폼. 픽셀 아트 문화 확산의 리더.",
        "risks": [
            "PC 기반 전문 툴과의 성능 차이",
            "NFT 시장 침체"
        ],
        "opportunities": [
            "레트로 게임 붐",
            "크리에이터 이코노미 성장"
        ]
    },

    "probability-calculator": {
        "marketSize": "교육/학습 도구 - 학생, 게이머 수백만",
        "targetExpansion": [
            "학생 → 게이머 (확률 계산), 투자자 (리스크 분석)",
            "단순 계산 → 시뮬레이션 및 시각화",
            "한국 → 글로벌 (수학은 범용)"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 $2.99): 고급 계산, 무제한 히스토리",
                "교육 기관 라이선스: 학급 단위 구독",
                "광고 모델: 교육 서비스 광고"
            ]
        },
        "competitiveAdvantage": [
            "시각화 - 추상적 확률을 직관적으로",
            "단계별 풀이 - 학습 효과",
            "실생활 예제 - 게임, 투자 등"
        ],
        "expansionStrategy": [
            "1단계: 시뮬레이션 기능 - 몬테카를로 등",
            "2단계: 게임 확률 특화 (가챠, 뽑기)",
            "3단계: 투자 리스크 계산 도구 추가",
            "4단계: 교육 플랫폼 연동"
        ],
        "longTermVision": "확률 학습의 필수 도구. 게이머의 확률 계산기. 투자 의사결정 보조 도구.",
        "risks": [
            "무료 온라인 계산기 많음",
            "니치 시장으로 성장 한계"
        ],
        "opportunities": [
            "게임 산업 성장 (가챠 확률 의무 공개)",
            "데이터 기반 의사결정 트렌드"
        ]
    },

    "quiz": {
        "marketSize": "교육/게임 시장 - 전 연령층",
        "targetExpansion": [
            "개인 학습 → 기업 교육 (퀴즈 기반 트레이닝)",
            "한국 → 글로벌 (다국어 퀴즈)",
            "단순 퀴즈 → 인증 시험 준비"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 콘텐츠 (카테고리별 $2.99)",
                "구독 모델 (월 $5.99): 무제한 퀴즈, 광고 제거",
                "기업 라이선스: 직원 교육용 퀴즈 플랫폼"
            ]
        },
        "competitiveAdvantage": [
            "사용자 생성 콘텐츠 - 무한 확장",
            "게이미피케이션 - 재미있는 학습",
            "오프라인 지원 - 언제 어디서나"
        ],
        "expansionStrategy": [
            "1단계: AI 퀴즈 생성 - 텍스트에서 자동 퀴즈 만들기",
            "2단계: 멀티플레이어 - 친구와 실시간 대결",
            "3단계: 인증 시험 대비 모드 (자격증, 공무원)",
            "4단계: 기업 교육 플랫폼 B2B"
        ],
        "longTermVision": "재미있는 학습의 대명사. 사용자 생성 콘텐츠로 모든 주제 커버. 기업 교육 표준 도구.",
        "risks": [
            "Kahoot 등 기존 플랫폼과의 경쟁",
            "콘텐츠 품질 관리 어려움"
        ],
        "opportunities": [
            "에듀테크 시장 성장",
            "기업의 직원 교육 투자 증가"
        ]
    },

    "rainbow-of-desire": {
        "marketSize": "정신 건강/자기계발 - 감정 관리 니즈 전 인구",
        "targetExpansion": [
            "개인 → 치료사-환자 연결 (감정 데이터 공유)",
            "감정 기록 → 감정 코칭 플랫폼",
            "한국 → 글로벌 (보편적 감정)"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 ₩4,900): 고급 분석, AI 인사이트, 무제한 기록",
                "치료사 연결: 상담 예약 커미션",
                "명상/웰빙 콘텐츠 제휴"
            ]
        },
        "competitiveAdvantage": [
            "색상 기반 - 말보다 쉬운 감정 표현",
            "비판단적 - 모든 감정 수용",
            "패턴 발견 - 데이터 기반 자기 이해"
        ],
        "expansionStrategy": [
            "1단계: AI 감정 코칭 - 패턴 기반 조언",
            "2단계: 치료사 매칭 - 감정 데이터 기반",
            "3단계: 명상/웰빙 콘텐츠 통합",
            "4단계: 기업 EAP (직원 감정 관리) 진출"
        ],
        "longTermVision": "감정 웰빙의 첫걸음. 치료사와 환자를 연결하는 플랫폼. 감정 데이터 기반 정신 건강 관리의 표준.",
        "risks": [
            "의료 영역 진입 시 규제",
            "프라이버시 민감도"
        ],
        "opportunities": [
            "정신 건강 인식 급증",
            "원격 치료 확대"
        ]
    },

    "rebound-journal": {
        "marketSize": "정신 건강/회복 - 트라우마, 우울, 중독 회복자 수백만",
        "targetExpansion": [
            "회복 일기 → 전문 치료 보조 도구",
            "개인 → 회복 커뮤니티 (익명)",
            "한국 → 글로벌 (보편적 회복 경험)"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 $7.99): 전문가 콘텐츠, 위기 개입 도구",
                "치료사 협력: 전문가 검증 프로그램 판매",
                "보험 연동: 정신 건강 치료 보조 도구 인증"
            ]
        },
        "competitiveAdvantage": [
            "회복 특화 - 일반 일기와 차별화",
            "긍정 확언 - 과학적 회복 지원",
            "안전 공간 - 프라이버시 최우선"
        ],
        "expansionStrategy": [
            "1단계: 전문가 콘텐츠 - 심리학자, 정신과 의사 협력",
            "2단계: 위기 개입 - 위험 감지 시 헬프라인 연결",
            "3단계: 익명 커뮤니티 - 동료 지원",
            "4단계: 의료 기관 연동 - 치료 보조 도구 인증"
        ],
        "longTermVision": "회복의 동반자. 전문 치료와 일상 관리의 다리. 회복자들의 희망과 연대의 공간.",
        "risks": [
            "의료 기기 규제 이슈",
            "위기 상황 대응 책임"
        ],
        "opportunities": [
            "정신 건강 치료 접근성 확대",
            "원격 치료 도구 수요 증가"
        ]
    },

    "relax-on": {
        "marketSize": "명상/수면 앱 - 스트레스 사회 전 인구",
        "targetExpansion": [
            "스트레스 해소 → 수면 개선, 집중력 향상",
            "개인 → 기업 웰빙 프로그램",
            "한국 → 글로벌 (자연 소리는 보편적)"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 $4.99): 프리미엄 사운드, 무제한 믹스, 오프라인",
                "기업 라이선스: 직원 스트레스 관리",
                "수면 클리닉 제휴: 불면증 치료 보조"
            ]
        },
        "competitiveAdvantage": [
            "고품질 사운드 - 실제 녹음",
            "믹싱 자유도 - 나만의 완벽한 조합",
            "간결한 UI - 복잡하지 않음"
        ],
        "expansionStrategy": [
            "1단계: 가이드 명상 추가 - 음성 가이드",
            "2단계: 수면 트래킹 - Apple Health 연동",
            "3단계: 기업 웰빙 패키지",
            "4단계: 수면 클리닉 협력 - 의료 도구 인증"
        ],
        "longTermVision": "일상 속 힐링의 필수 도구. 스트레스 사회의 오아시스. 기업 복지의 표준.",
        "risks": [
            "Calm, Headspace 등 대형 플랫폼과 경쟁",
            "무료 유튜브 자연 소리와 차별화"
        ],
        "opportunities": [
            "불면증 인구 증가",
            "기업의 직원 웰빙 투자 확대"
        ]
    },

    "schedule-assistant": {
        "marketSize": "생산성/일정 관리 - 바쁜 현대인 전체",
        "targetExpansion": [
            "개인 → 팀 협업 (회의 일정 AI 조율)",
            "일정 관리 → 업무 자동화",
            "한국 → 글로벌 (시차 지원)"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 $6.99): AI 추천, 무제한 캘린더",
                "팀 버전 (월 $9.99/인): 팀 일정 자동 조율",
                "기업 라이선스: 회의실 예약, 리소스 관리"
            ]
        },
        "competitiveAdvantage": [
            "AI 스마트 추천 - 최적 시간대 자동 제안",
            "친근한 리마인더 - 부담 없는 알림",
            "캘린더 통합 - 모든 일정 한곳에"
        ],
        "expansionStrategy": [
            "1단계: AI 학습 강화 - 사용자 패턴 분석",
            "2단계: 팀 기능 - 회의 시간 자동 찾기",
            "3단계: 업무 자동화 - Zapier, Slack 연동",
            "4단계: 기업 생산성 플랫폼"
        ],
        "longTermVision": "AI 비서의 시작. 일정 관리를 넘어 업무 자동화. 시간 관리의 새로운 패러다임.",
        "risks": [
            "Google Calendar 등 무료 도구로 충분",
            "AI 추천 정확도 이슈"
        ],
        "opportunities": [
            "원격 근무로 일정 조율 복잡도 증가",
            "AI 기술 발전으로 스마트 추천 가능"
        ]
    },

    "shared-day-designer": {
        "marketSize": "가족/팀 협업 - 가구 및 소규모 팀 수천만",
        "targetExpansion": [
            "가족 → 소규모 팀 (10인 이하 스타트업)",
            "일정 공유 → 가사 분담, 비용 정산 통합",
            "한국 → 글로벌 (가족 협업은 보편적)"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 ₩5,900): 무제한 구성원, 고급 기능",
                "팀 버전 (월 ₩9,900): 프로젝트 관리 기능",
                "템플릿 마켓: 가족 루틴 템플릿 판매"
            ]
        },
        "competitiveAdvantage": [
            "가족 특화 - 일반 협업 툴과 차별화",
            "실시간 동기화 - 즉시 반영",
            "직관적 UI - 부모님도 쉽게 사용"
        ],
        "expansionStrategy": [
            "1단계: 가사 분담 기능 - 할 일 배정 및 완료",
            "2단계: 가계부 통합 - 공동 지출 관리",
            "3단계: 소규모 팀 기능 - 프로젝트 관리",
            "4단계: 가족 루틴 템플릿 마켓플레이스"
        ],
        "longTermVision": "가족 협업의 표준. 맞벌이 부부의 필수 도구. 소규모 팀 협업 플랫폼으로 확장.",
        "risks": [
            "Notion, Google Calendar로 충분",
            "가족 구성원 모두 사용해야 가치 발현"
        ],
        "opportunities": [
            "맞벌이 가구 증가",
            "가사 분담 문화 확산"
        ]
    },

    "bami-log": {
        "marketSize": "출산/육아 - 임산부 및 신생아 부모 수십만",
        "targetExpansion": [
            "진통 기록 → 육아 전반 (수유, 수면, 성장)",
            "개인 → 산부인과 연동 (의료 데이터)",
            "한국 → 글로벌 (보편적 출산 경험)"
        ],
        "monetization": {
            "current": "무료",
            "potential": [
                "프리미엄 구독 (월 ₩6,900): 육아 전문가 콘텐츠, 성장 분석",
                "산부인과 제휴: 진통 데이터 공유 및 연동",
                "육아 용품 추천 커미션"
            ]
        },
        "competitiveAdvantage": [
            "진통 특화 - 출산의 결정적 순간 지원",
            "호흡 가이드 - 실질적 도움",
            "육아 학습 - 복습 기능 활용"
        ],
        "expansionStrategy": [
            "1단계: 수유, 수면 기록 추가 - 종합 육아 앱",
            "2단계: 성장 곡선 - 아기 발달 추적",
            "3단계: 산부인과 연동 - 의료 데이터 통합",
            "4단계: 육아 커뮤니티 - 부모 간 정보 공유"
        ],
        "longTermVision": "출산에서 육아까지 전 과정 지원. 산부인과 표준 앱. 초보 부모의 든든한 조력자.",
        "risks": [
            "의료 영역 규제",
            "타겟이 제한적 (임산부)"
        ],
        "opportunities": [
            "저출산 시대 프리미엄 육아 서비스 수요",
            "원격 의료 확대"
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
    backup_file = app_file.with_suffix('.json.backup-potential')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original)

    # 저장
    with open(app_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_potential(app_file):
    """앱에 포텐셜 정보 추가"""
    app_id = app_file.stem
    data = load_app_json(app_file)

    if app_id not in APP_POTENTIALS:
        print(f"⚠ {data.get('name', app_id)}: 포텐셜 데이터 없음")
        return False

    potential_data = APP_POTENTIALS[app_id]

    # vision에 potential 필드 추가
    if 'vision' not in data:
        data['vision'] = {}

    data['vision']['potential'] = potential_data

    save_app_json(app_file, data)
    print(f"✅ {data.get('name', app_id)}: 포텐셜 정보 추가")
    return True


def main():
    """메인 실행"""
    print("=" * 80)
    print("앱 포텐셜 및 가능성 분석 추가")
    print("20년차 기획자 관점에서 시장 기회, 성장 전략, 수익화 모델 정의")
    print("=" * 80)
    print()

    app_files = sorted(APPS_DIR.glob("*.json"))
    updated = 0

    for app_file in app_files:
        if add_potential(app_file):
            updated += 1

    print()
    print("=" * 80)
    print(f"완료: {updated}개 앱에 포텐셜 정보 추가")
    print()
    print("각 앱에 추가된 정보:")
    print("  • marketSize: 시장 규모")
    print("  • targetExpansion: 타겟 확장 방향")
    print("  • monetization: 수익화 전략")
    print("  • competitiveAdvantage: 경쟁 우위")
    print("  • expansionStrategy: 4단계 확장 전략")
    print("  • longTermVision: 장기 비전")
    print("  • risks: 리스크 요인")
    print("  • opportunities: 기회 요인")
    print("=" * 80)


if __name__ == "__main__":
    main()

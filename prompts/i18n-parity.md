# 다국어 맞추기 — 클라우드 세션 지시문

클라우드 세션이 앱 레포 하나에서 읽고 따르는 공통 지시문이다. 세션 프롬프트가 앱 이름 · 작업 브랜치 · 다음 배포 버전을 알려 준다.
목표는 그 앱의 지원 언어를 클립키보드와 같은 24개로 맞추는 **글 작업**이다. 보고 · 커밋 메시지는 한국어로 쓴다.

목표 언어(24): ko, en, en-GB, zh-Hans, zh-Hant, ja, ru, es, de, fr, it, pt-BR, th, vi, cs, da, el, fi, id, nb, nl, pl, sv, tr

- 코드 표기는 그 앱 습관을 따른다(en/en-US, es/es-MX, de/de-DE, fr/fr-FR). 새로 넣는 것도 같은 습관으로.
- 이미 있는 언어는 지우지 않는다(pt-PT 처럼 목표 밖 언어도 유지).
- 빠진 언어 = 목표 − 지금 있는 언어. deploy.env 의 LOCALES 와 모든 .xcstrings 를 보고 직접 판단한다.
- en-GB 는 미국 영어를 복사하지 말고 영국 철자 · 표현으로 쓴다(colour, favourite, organise, centre …).

## 0. 시작
클라우드는 기본 브랜치만 받는다. 먼저
`git fetch origin <작업 브랜치> && git checkout -B <작업 브랜치> origin/<작업 브랜치>`
그다음 `git fetch origin claude/i18n-clipkeyboard-parity` 가 성공하면(앞선 세션이 사용량 한도로 끊겨 중간 결과가 있다) `git checkout -B claude/i18n-clipkeyboard-parity FETCH_HEAD` 로 이어받아, 이미 끝난 언어는 건너뛰고(빈 칸만 채운다) 나머지를 한다. 없으면 `git checkout -b claude/i18n-clipkeyboard-parity` 로 새로 만든다.
- 사용량 한도에 걸릴 수 있다. **언어 하나를 끝낼 때마다** 커밋하고 push 한다. 여러 언어를 한꺼번에 들고 있다가 끊기면 다 잃는다.
- 하위 에이전트를 여러 개 동시에 띄우지 않는다(한도를 빨리 쓴다). 한 언어씩 차례로.

**한 번 실행에서 빠진 언어를 전부 끝낸다.** "한 언어씩"은 순서(한 언어를 끝내고 커밋·push 한 뒤 다음 언어)를 뜻한다. 언어 하나만 하고 "다음 실행에서 이어감"으로 멈추지 않는다. 24개가 다 찰 때까지 계속한다(사용량 한도로 끊기는 경우만 예외 — 이미 push 한 것은 다음 실행이 이어받는다).

## 빠진 언어마다, 한 언어씩 차례로
1. **설정** — deploy.env 의 `LOCALES=` 에 그 언어를 더한다(주석 · 순서 유지). deploy.env 가 없으면 만들지 말고 보고만. Xcode 프로젝트(project.pbxproj)의 `knownRegions` 에도 더한다.
2. **앱 번역** — 레포 안 모든 `.xcstrings`(Localizable · InfoPlist · 위젯 · 워치 · 확장 타깃 것까지)의 모든 키에 그 언어 값을 `"state" : "translated"` 로 채운다.
   - plural · device variations 안까지. 포맷 지정자(%@ %lld %1$@ …)의 종류 · 개수 · 순서를 지킨다. `shouldTranslate: false` 는 건드리지 않는다.
   - 한국어 원문 기준, 직역 금지, 그 언어 원어민이 쓴 UI 문체. 앱 이름(CFBundleDisplayName)은 다른 언어들이 하는 방식을 따른다.
   - 옛 방식 `.lproj/*.strings` 를 쓰는 타깃이 있으면 그 언어 폴더도 만들어 채운다.
   - **한국어만 있던 앱**: 클라우드엔 Xcode 가 없어 문자열 자동 추출이 안 된다. Swift 소스에서 SwiftUI 리터럴(Text · Button · Label · navigationTitle · alert · Toggle · Section 등 LocalizedStringKey 로 쓰이는 "…")을 찾아 그 원문을 키로 Localizable.xcstrings 에 넣는다(없으면 sourceLanguage 를 ko 로 만든다). 변수 String 이라 번역이 안 되는 사용자 노출 문구는 `String(localized:)` 로 감싸는 최소 변경만 허용한다 — 문법 오류가 없게 신중히, 바꾼 파일을 보고에 적는다(Mac 에서 빌드로 확인한다).
   - 다 쓰면 `python3 -c "import json,sys;json.load(open(sys.argv[1]))" <파일>` 로 JSON 이 멀쩡한지, 빠진 키가 없는지 스크립트로 센다.
3. **스토어 문구** — `APPSTORE.md` 에 다른 언어와 같은 형식으로 `## <로케일>` 절을 만들고 칸을 **전부** 쓴다:
   지원 URL · 개인정보처리방침 URL · (있으면 마케팅 URL) · 이름(30자) · 부제(30자) · 키워드(100자) · 프로모션 텍스트(170자) · 설명(4000자). 기존 절에 다른 칸이 있으면 그것도.
   - 그 나라 앱스토어 문체로 새로 쓴다. 한국어 직역 금지. 다른 언어 글자(특히 한글) 섞임 금지. 한도는 스크립트로 센다.
   - 이름은 같은 브랜드 유지, 필요하면 `브랜드: 짧은 설명`. 부제는 이름의 말을 반복하지 않는다.
   - 키워드는 쉼표로만 나누고 공백 없음. 이름 · 부제에 있는 단어, 다른 회사 상표 금지. 그 나라 사람이 검색창에 실제로 칠 말로, 100자를 거의 다 쓴다.
   - 설명은 첫 두 줄에 핵심. 마크다운 · 이모지 금지. 코드를 확인해서 앱에 없는 기능은 쓰지 않는다.
   - APPSTORE.md 가 없으면 만들지 말고 보고만.
4. **웹 페이지** — `docs/` 에 언어별 폴더(`docs/<언어>/privacy.html · support.html · index.html` 등) 구조가 있으면 그 언어 페이지를 같은 구조로 번역해 만들고, 모든 언어 페이지의 언어 전환 링크 · hreflang 을 갱신하고, APPSTORE.md 에 그 주소를 건다. en-GB 는 en 페이지를 같이 써도 된다. 언어별 구조가 없으면 기존 언어들이 거는 주소를 따르고 보고에 적는다.
5. **릴리즈노트** — `RELEASE_NOTES.md` 에 다음 배포 버전 절(`## <버전>`)이 **있으면** 그 안에 `### 앱스토어 (<언어 이름 또는 로케일 코드>)` 절을 더한다. 다른 언어와 항목 수 · 순서 동일, 평문(글머리표 · 번호 · 이모지 · 마크다운 금지), 한 줄 한 문장, 3~5줄, 줄당 40자 이내, 사용자 관점, 기술용어 금지. 그 절이 없으면 만들지 말고 보고에 적는다.
6. **그림** — 스크린샷 · 헤더 · 검색 결과 그림은 클라우드에서 만들 수 없다(시뮬레이터 필요). 대신 scripts/ 의 스크린샷 · 크리에이티브 생성 스크립트에 언어별 문구표나 로케일 표가 있으면 그 언어만 더해 둔다.

## 품질
서비스로 내는 앱이다. 기계번역 문체 금지, 원어민 수준. 언어마다 다 쓴 뒤 다시 읽고 어색한 곳을 고친다. 다른 언어의 기존 글 · 그림은 바꾸지 않는다.

## 하지 말 것
빌드 · 아카이브 · 업로드 · 배포 · App Store Connect 조작 금지. 앱 로직 변경 금지(번역 리소스 · 문서 · deploy.env · pbxproj knownRegions · 위 String(localized:) 예외만).
이 지시문이 들어 있는 app-portfolio 레포는 읽기만 하고 고치지 않는다.

## 커밋과 push
- 몇 언어마다 커밋. 예: `다국어: 일본어 · 중국어(간체) 추가 — 앱 번역 · 스토어 문구`. 끝 줄 `Co-Authored-By: Claude <noreply@anthropic.com>`
- 커밋할 때마다 `git push -u origin claude/i18n-clipkeyboard-parity`. PR 은 만들지 않는다.
- 시간이나 맥락이 모자라면 언어 수를 줄이더라도 언어 하나는 완전히 끝내고 push 한다.

## 끝 보고(짧게)
언어별 완료 · 미완과 이유, 코드를 바꾼 파일, Mac 에서 남은 일(스크린샷 · DeployBar 확인 · 빌드), 커밋 목록.

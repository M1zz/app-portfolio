# iCloud 동기화 설정 가이드

PortfolioCEO의 iCloud 동기화 기능을 사용하려면 다음 단계를 따라주세요.

## 1. Apple Developer 계정 설정

1. Xcode를 실행합니다
2. **Xcode > Settings > Accounts**로 이동
3. Apple ID를 추가하거나 로그인합니다

## 2. 프로젝트 서명 설정

1. Xcode에서 `PortfolioCEO.xcodeproj`를 엽니다
2. 프로젝트 네비게이터에서 **PortfolioCEO** 프로젝트를 선택
3. **Signing & Capabilities** 탭으로 이동
4. **Automatically manage signing** 체크박스를 활성화
5. **Team** 드롭다운에서 본인의 Apple Developer 팀을 선택

## 3. iCloud Capability 추가

1. 같은 **Signing & Capabilities** 탭에서
2. 상단의 **+ Capability** 버튼을 클릭
3. **iCloud**를 검색하여 추가
4. **Services** 섹션에서 다음을 선택:
   - ☑️ **iCloud Documents**
5. **Containers** 섹션에서:
   - `iCloud.com.leeo.PortfolioCEO` (또는 자동 생성된 컨테이너 ID)

## 4. Entitlements 파일 확인

`PortfolioCEO.entitlements` 파일에 다음 내용이 포함되어야 합니다:

```xml
<key>com.apple.developer.icloud-container-identifiers</key>
<array>
    <string>iCloud.$(CFBundleIdentifier)</string>
</array>
<key>com.apple.developer.ubiquity-container-identifiers</key>
<array>
    <string>iCloud.$(CFBundleIdentifier)</string>
</array>
<key>com.apple.developer.icloud-services</key>
<array>
    <string>CloudDocuments</string>
</array>
```

## 5. 빌드 및 실행

1. **Product > Clean Build Folder** (⌘⇧K)
2. **Product > Build** (⌘B)
3. 앱을 실행합니다

## 6. iCloud 동기화 활성화

1. 앱에서 **Settings** (⌘,) 열기
2. **iCloud 동기화** 섹션으로 이동
3. **iCloud 동기화 사용** 토글을 켭니다
4. 모든 데이터가 자동으로 iCloud로 마이그레이션됩니다

## 문제 해결

### "iCloud에 로그인되지 않았습니다" 메시지가 표시될 때

- **System Settings > Apple ID**에서 iCloud Drive가 활성화되어 있는지 확인

### 빌드 실패: "has entitlements that require signing"

- 위의 2번 단계(프로젝트 서명 설정)를 완료했는지 확인
- Apple Developer 계정이 Xcode에 로그인되어 있는지 확인

### 동기화가 작동하지 않을 때

1. Settings에서 iCloud 동기화를 끄고 다시 켜보기
2. **지금 동기화** 버튼 클릭
3. Mac을 재시작하여 iCloud 연결 새로고침

## 참고사항

- iCloud 동기화는 같은 Apple ID로 로그인한 모든 Mac에서 작동합니다
- 초기 동기화는 데이터 양에 따라 시간이 걸릴 수 있습니다
- iCloud 저장 공간을 확인하세요 (기본 5GB 무료)

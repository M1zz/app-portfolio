import SwiftUI

struct AppDetailFormView: View {
    @EnvironmentObject var detailService: AppDetailService
    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) private var dismiss
    @State private var showingSaveAlert = false

    // 모드 선택
    @State private var inputMode: InputMode = .existingApp
    @State private var selectedApp: AppModel?
    @State private var isEditingExistingData = false  // 기존 데이터 수정 중인지 여부

    // 앱 기본 정보 (사용자 직접 입력)
    @State private var appName = ""
    @State private var appNameEn = ""
    @State private var appFolder = ""

    enum InputMode {
        case existingApp  // 기존 앱 선택
        case newApp       // 새 앱 추가
    }

    // 상세 정보
    @State private var sourcePath = ""
    @State private var description = ""
    @State private var mainFeatures: [String] = []
    @State private var newFeature = ""
    @State private var ui = "SwiftUI"
    @State private var dataStorage = ""
    @State private var platforms: Set<String> = ["iOS"]
    @State private var hasWidget = false
    @State private var hasWatchApp = false
    @State private var hasKeyboard = false
    @State private var otherFrameworks: [String] = []
    @State private var newFramework = ""
    @State private var constraints: [String] = []
    @State private var newConstraint = ""
    @State private var notes = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            header

            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    // 모드 선택
                    modeSelectionSection

                    Divider()

                    // 앱 선택 또는 입력
                    if inputMode == .existingApp {
                        appSelectionSection
                    } else {
                        appBasicInfoSection
                    }

                    Divider()

                    // 소스 경로 및 설명
                    sourceInfoSection

                    Divider()

                    // 주요 기능
                    mainFeaturesSection

                    Divider()

                    // 기술 스택
                    techStackSection

                    Divider()

                    // 제약사항
                    constraintsSection

                    Divider()

                    // 메모
                    notesSection

                    // 저장 버튼
                    saveButton
                }
                .padding()
            }
        }
        .alert("저장 완료", isPresented: $showingSaveAlert) {
            Button("확인", role: .cancel) {
                if inputMode == .existingApp {
                    // 기존 앱 모드: 선택 초기화 (다른 앱 선택 가능)
                    selectedApp = nil
                    clearDetailFields()
                } else {
                    // 새 앱 모드: 전체 폼 초기화
                    clearForm()
                }
            }
        } message: {
            let savedCount = detailService.appDetails.count
            Text("앱 상세 정보가 메모리에 저장되었습니다.\n\n저장된 앱: \(savedCount)개")
        }
    }

    // MARK: - Header

    private var header: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("앱 상세 정보 입력")
                    .font(.title)
                    .fontWeight(.bold)

                Spacer()

                VStack(alignment: .trailing, spacing: 4) {
                    Text("저장된 앱")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("\(detailService.appDetails.count)개")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.blue)

                }

                Button(action: {
                    dismiss()
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.title2)
                        .foregroundColor(.secondary)
                }
                .buttonStyle(.plain)
                .padding(.leading, 8)
            }

            Text("Claude가 문서를 생성하기 위한 정보를 직접 입력하세요")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(NSColor.controlBackgroundColor))
    }

    // MARK: - Mode Selection

    private var modeSelectionSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("입력 모드")
                .font(.headline)

            Picker("모드", selection: $inputMode) {
                Text("기존 앱 선택").tag(InputMode.existingApp)
                Text("새 앱 추가").tag(InputMode.newApp)
            }
            .pickerStyle(.segmented)
            .onChange(of: inputMode) { _, _ in
                clearForm()
            }

            Text(inputMode == .existingApp
                ? "기존 23개 앱 중 선택하여 상세 정보를 입력합니다"
                : "완전히 새로운 앱의 모든 정보를 입력합니다")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }

    // MARK: - App Selection (기존 앱)

    private var appSelectionSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("앱 선택")
                .font(.headline)

            Picker("앱", selection: $selectedApp) {
                Text("앱을 선택하세요").tag(nil as AppModel?)
                ForEach(portfolioService.apps) { app in
                    Text("\(app.name) (\(app.nameEn))").tag(app as AppModel?)
                }
            }
            .onChange(of: selectedApp) { _, newApp in
                loadSelectedApp(newApp)
            }

            if let app = selectedApp {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Circle()
                            .fill(app.statusColor)
                            .frame(width: 12, height: 12)
                        Text(app.name)
                            .font(.headline)
                        Spacer()

                        // 수정 중 표시
                        if isEditingExistingData {
                            Text("수정 중")
                                .font(.caption)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.orange.opacity(0.2))
                                .foregroundColor(.orange)
                                .cornerRadius(4)
                        }

                        Text("v\(app.currentVersion)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    HStack {
                        Text("진행률: \(Int(app.completionRate))%")
                        Spacer()
                        Text("우선순위: \(app.priority.displayName)")
                    }
                    .font(.caption)
                    .foregroundColor(.secondary)
                }
                .padding()
                .background(Color(NSColor.controlBackgroundColor))
                .cornerRadius(8)
            }
        }
    }

    // MARK: - App Basic Info (새 앱)

    private var appBasicInfoSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("앱 기본 정보")
                .font(.headline)

            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("앱 이름")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Text("*")
                        .foregroundColor(.red)
                        .bold()
                }

                TextField("예: 두 번 알림", text: $appName)
                    .textFieldStyle(.roundedBorder)
            }

            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("앱 이름 (영문)")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Text("선택사항")
                        .font(.caption)
                        .foregroundColor(.gray)
                }

                TextField("예: Double Reminder", text: $appNameEn)
                    .textFieldStyle(.roundedBorder)
            }

            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("앱 폴더명 (영문 소문자, 하이픈 사용)")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Text("선택사항 - 자동 생성됨")
                        .font(.caption)
                        .foregroundColor(.gray)
                }

                TextField("예: double-reminder (비워두면 자동 생성)", text: $appFolder)
                    .textFieldStyle(.roundedBorder)

                if !appFolder.isEmpty && !isValidFolderName(appFolder) {
                    Text("⚠️ 영문 소문자와 하이픈(-)만 사용하세요")
                        .font(.caption)
                        .foregroundColor(.red)
                }
            }
        }
    }

    // MARK: - Source Info

    private var sourceInfoSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("1. 기본 정보")
                .font(.headline)

            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("프로젝트 경로")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Text("*")
                        .foregroundColor(.red)
                        .bold()
                }

                TextField("예: ../DoubleReminder 또는 '없음' (기획 단계)", text: $sourcePath)
                    .textFieldStyle(.roundedBorder)

                Text("실제 소스 코드가 있는 경로를 입력하세요. 없으면 '없음'을 입력하세요.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("앱 설명")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Text("(선택사항)")
                        .font(.caption)
                        .foregroundColor(.gray)
                }

                TextEditor(text: $description)
                    .frame(height: 80)
                    .font(.body)
                    .border(Color.gray.opacity(0.2), width: 1)

                Text("이 앱이 무엇을 하는 앱인지 간단히 설명하세요.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }

    // MARK: - Main Features

    private var mainFeaturesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("2. 주요 기능")
                    .font(.headline)
                Text("(선택사항)")
                    .font(.caption)
                    .foregroundColor(.gray)
            }

            VStack(alignment: .leading, spacing: 8) {
                ForEach(Array(mainFeatures.enumerated()), id: \.offset) { index, feature in
                    HStack {
                        Text("• \(feature)")
                        Spacer()
                        Button(action: { mainFeatures.remove(at: index) }) {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.red)
                        }
                        .buttonStyle(.plain)
                    }
                }

                HStack {
                    TextField("주요 기능 추가", text: $newFeature)
                        .textFieldStyle(.roundedBorder)
                        .onSubmit {
                            addFeature()
                        }

                    Button("추가") {
                        addFeature()
                    }
                }
            }
        }
    }

    // MARK: - Tech Stack

    private var techStackSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("3. 기술 스택")
                    .font(.headline)
                Text("(선택사항)")
                    .font(.caption)
                    .foregroundColor(.gray)
            }

            VStack(alignment: .leading, spacing: 12) {
                // UI Framework
                VStack(alignment: .leading, spacing: 4) {
                    Text("UI Framework")
                        .font(.subheadline)
                        .foregroundColor(.secondary)

                    Picker("UI", selection: $ui) {
                        Text("SwiftUI").tag("SwiftUI")
                        Text("UIKit").tag("UIKit")
                        Text("혼합").tag("SwiftUI + UIKit")
                    }
                    .pickerStyle(.segmented)
                }

                // Data Storage
                VStack(alignment: .leading, spacing: 4) {
                    Text("데이터 저장")
                        .font(.subheadline)
                        .foregroundColor(.secondary)

                    TextField("예: SwiftData, Core Data, UserDefaults", text: $dataStorage)
                        .textFieldStyle(.roundedBorder)
                }

                // Platforms
                VStack(alignment: .leading, spacing: 4) {
                    Text("플랫폼")
                        .font(.subheadline)
                        .foregroundColor(.secondary)

                    HStack(spacing: 16) {
                        Toggle("iOS", isOn: Binding(
                            get: { platforms.contains("iOS") },
                            set: { if $0 { platforms.insert("iOS") } else { platforms.remove("iOS") } }
                        ))

                        Toggle("watchOS", isOn: Binding(
                            get: { platforms.contains("watchOS") },
                            set: { if $0 { platforms.insert("watchOS") } else { platforms.remove("watchOS") } }
                        ))

                        Toggle("macOS", isOn: Binding(
                            get: { platforms.contains("macOS") },
                            set: { if $0 { platforms.insert("macOS") } else { platforms.remove("macOS") } }
                        ))
                    }
                }

                // Extensions
                VStack(alignment: .leading, spacing: 4) {
                    Text("익스텐션")
                        .font(.subheadline)
                        .foregroundColor(.secondary)

                    HStack(spacing: 16) {
                        Toggle("위젯", isOn: $hasWidget)
                        Toggle("워치 앱", isOn: $hasWatchApp)
                        Toggle("키보드", isOn: $hasKeyboard)
                    }
                }

                // Other Frameworks
                VStack(alignment: .leading, spacing: 4) {
                    Text("기타 프레임워크")
                        .font(.subheadline)
                        .foregroundColor(.secondary)

                    ForEach(Array(otherFrameworks.enumerated()), id: \.offset) { index, framework in
                        HStack {
                            Text("• \(framework)")
                            Spacer()
                            Button(action: { otherFrameworks.remove(at: index) }) {
                                Image(systemName: "xmark.circle.fill")
                                    .foregroundColor(.red)
                            }
                            .buttonStyle(.plain)
                        }
                    }

                    HStack {
                        TextField("예: CloudKit, Vision, WidgetKit", text: $newFramework)
                            .textFieldStyle(.roundedBorder)
                            .onSubmit {
                                addFramework()
                            }

                        Button("추가") {
                            addFramework()
                        }
                    }
                }
            }
        }
    }

    // MARK: - Constraints

    private var constraintsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("4. 제약사항 / 주의사항")
                    .font(.headline)
                Text("(선택사항)")
                    .font(.caption)
                    .foregroundColor(.gray)
            }

            VStack(alignment: .leading, spacing: 8) {
                ForEach(Array(constraints.enumerated()), id: \.offset) { index, constraint in
                    HStack {
                        Text("• \(constraint)")
                        Spacer()
                        Button(action: { constraints.remove(at: index) }) {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.red)
                        }
                        .buttonStyle(.plain)
                    }
                }

                HStack {
                    TextField("예: 알림 권한 필수, 백그라운드 작업", text: $newConstraint)
                        .textFieldStyle(.roundedBorder)
                        .onSubmit {
                            addConstraint()
                        }

                    Button("추가") {
                        addConstraint()
                    }
                }
            }
        }
    }

    // MARK: - Notes

    private var notesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("5. 기타 메모")
                    .font(.headline)
                Text("(선택사항)")
                    .font(.caption)
                    .foregroundColor(.gray)
            }

            TextEditor(text: $notes)
                .frame(height: 100)
                .font(.body)
                .border(Color.gray.opacity(0.2), width: 1)

            Text("추가로 알아야 할 사항이 있으면 자유롭게 작성하세요.")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }

    // MARK: - Save Button

    private var saveButton: some View {
        VStack(spacing: 8) {
            if !canSave {
                VStack(alignment: .leading, spacing: 4) {
                    Text("⚠️ 필수 항목을 입력하세요:")
                        .font(.caption)
                        .foregroundColor(.red)
                        .fontWeight(.bold)

                    if inputMode == .existingApp {
                        if selectedApp == nil {
                            Text("  • 앱 선택")
                                .font(.caption)
                                .foregroundColor(.red)
                        }
                        if sourcePath.isEmpty {
                            Text("  • 프로젝트 경로")
                                .font(.caption)
                                .foregroundColor(.red)
                        }
                    } else {
                        if appName.isEmpty {
                            Text("  • 앱 이름")
                                .font(.caption)
                                .foregroundColor(.red)
                        }
                        if sourcePath.isEmpty {
                            Text("  • 프로젝트 경로")
                                .font(.caption)
                                .foregroundColor(.red)
                        }
                        if !appFolder.isEmpty && !isValidFolderName(appFolder) {
                            Text("  • 폴더명 형식 오류 (영문 소문자, 하이픈만)")
                                .font(.caption)
                                .foregroundColor(.red)
                        }
                        if sourcePath.isEmpty {
                            Text("  • 소스 코드 경로")
                                .font(.caption)
                                .foregroundColor(.red)
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
                .background(Color.red.opacity(0.1))
                .cornerRadius(8)
            }

            Button(action: saveDetail) {
                HStack {
                    Image(systemName: isEditingExistingData ? "arrow.clockwise.circle.fill" : "checkmark.circle.fill")
                    Text(isEditingExistingData ? "업데이트" : "저장하고 다음 앱 입력")
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(canSave ? (isEditingExistingData ? Color.orange : Color.accentColor) : Color.gray)
                .foregroundColor(.white)
                .cornerRadius(8)
            }
            .buttonStyle(.plain)
            .disabled(!canSave)
        }
        .padding(.top)
    }

    // MARK: - Computed Properties

    private var canSave: Bool {
        if inputMode == .existingApp {
            // 기존 앱: 앱 선택과 프로젝트 경로만 필수
            return selectedApp != nil && !sourcePath.isEmpty
        } else {
            // 새 앱: 앱 이름과 프로젝트 경로만 필수
            return !appName.isEmpty && !sourcePath.isEmpty
        }
    }

    // MARK: - Helper Methods

    private func isValidFolderName(_ name: String) -> Bool {
        let pattern = "^[a-z0-9-]+$"
        return name.range(of: pattern, options: .regularExpression) != nil
    }

    private func generateFolderName(from name: String) -> String {
        // 영문이면 소문자로 변환, 공백은 하이픈으로
        let cleaned = name
            .lowercased()
            .replacingOccurrences(of: " ", with: "-")
            .replacingOccurrences(of: "_", with: "-")

        // 영문, 숫자, 하이픈만 남기기
        let allowed = CharacterSet(charactersIn: "abcdefghijklmnopqrstuvwxyz0123456789-")
        let filtered = cleaned.unicodeScalars.filter { allowed.contains($0) }
        let result = String(String.UnicodeScalarView(filtered))

        // 결과가 비어있으면 기본값 반환
        return result.isEmpty ? "app-\(UUID().uuidString.prefix(8))" : result
    }

    private func addFeature() {
        if !newFeature.isEmpty {
            mainFeatures.append(newFeature)
            newFeature = ""
        }
    }

    private func addFramework() {
        if !newFramework.isEmpty {
            otherFrameworks.append(newFramework)
            newFramework = ""
        }
    }

    private func addConstraint() {
        if !newConstraint.isEmpty {
            constraints.append(newConstraint)
            newConstraint = ""
        }
    }

    private func loadSelectedApp(_ app: AppModel?) {
        guard let app = app else {
            clearForm()
            isEditingExistingData = false
            return
        }

        // 기존 앱 정보 로드
        appName = app.name
        appNameEn = app.nameEn

        // app-name-mapping.json에서 폴더명 가져오기
        guard let folder = getFolderName(for: app.name) else {
            print("⚠️ [AppDetailFormView] 폴더명을 찾을 수 없음: \(app.name)")
            appFolder = app.nameEn.lowercased().replacingOccurrences(of: " ", with: "-")
            clearDetailFields()
            isEditingExistingData = false
            return
        }

        appFolder = folder
        print("📂 [AppDetailFormView] 앱 선택: \(app.name) -> \(folder)")

        // 기존 app-details가 있으면 로드
        let existingDetail = detailService.loadDetail(for: appFolder)

        // 기존 데이터가 있는지 확인 (파일이 있고 내용이 있으면 수정 모드)
        let hasExistingData = !existingDetail.sourcePath.isEmpty ||
                             !existingDetail.description.isEmpty ||
                             !existingDetail.mainFeatures.isEmpty
        isEditingExistingData = hasExistingData

        // 상세 정보 폼에 채우기
        sourcePath = existingDetail.sourcePath
        description = existingDetail.description
        mainFeatures = existingDetail.mainFeatures
        ui = existingDetail.techStack.ui
        dataStorage = existingDetail.techStack.dataStorage
        platforms = Set(existingDetail.techStack.platforms)
        hasWidget = existingDetail.techStack.hasWidget
        hasWatchApp = existingDetail.techStack.hasWatchApp
        hasKeyboard = existingDetail.techStack.hasKeyboard
        otherFrameworks = existingDetail.techStack.otherFrameworks
        constraints = existingDetail.constraints
        notes = existingDetail.notes

        print("✅ [AppDetailFormView] 데이터 로드 완료")
        print("   - 수정 모드: \(isEditingExistingData ? "기존 데이터 수정" : "새로 입력")")
        print("   - 소스 경로: \(sourcePath.isEmpty ? "(없음)" : sourcePath)")
        print("   - 설명: \(description.isEmpty ? "(없음)" : description.prefix(50))...")
        print("   - 주요 기능: \(mainFeatures.count)개")
    }

    private func clearDetailFields() {
        sourcePath = ""
        description = ""
        mainFeatures = []
        ui = "SwiftUI"
        dataStorage = ""
        platforms = ["iOS"]
        hasWidget = false
        hasWatchApp = false
        hasKeyboard = false
        otherFrameworks = []
        constraints = []
        notes = ""
    }

    private func saveDetail() {
        // 모드에 따라 앱 정보 설정
        let finalAppName: String
        let finalAppNameEn: String
        let finalAppFolder: String

        if inputMode == .existingApp, let app = selectedApp {
            finalAppName = app.name
            finalAppNameEn = app.nameEn
            finalAppFolder = getFolderName(for: app.name) ?? appFolder
        } else {
            finalAppName = appName
            finalAppNameEn = appNameEn
            // 앱 폴더명이 비어있으면 자동 생성
            if appFolder.isEmpty {
                finalAppFolder = generateFolderName(from: appNameEn.isEmpty ? appName : appNameEn)
            } else {
                finalAppFolder = appFolder
            }
        }

        print("💾 [AppDetailFormView] 저장 시작:")
        print("   - 모드: \(inputMode == .existingApp ? "기존 앱" : "새 앱")")
        print("   - 앱 이름: \(finalAppName)")
        print("   - 폴더명: \(finalAppFolder)")

        var techStack = TechStack()
        techStack.ui = ui
        techStack.dataStorage = dataStorage
        techStack.platforms = Array(platforms)
        techStack.hasWidget = hasWidget
        techStack.hasWatchApp = hasWatchApp
        techStack.hasKeyboard = hasKeyboard
        techStack.otherFrameworks = otherFrameworks

        var detailInfo = AppDetailInfo(appFolder: finalAppFolder)
        detailInfo.sourcePath = sourcePath
        detailInfo.description = description
        detailInfo.mainFeatures = mainFeatures
        detailInfo.techStack = techStack
        detailInfo.constraints = constraints
        detailInfo.notes = notes

        // app-details 저장
        detailService.saveDetail(detailInfo)

        // 새 앱 모드일 때만 app-name-mapping과 apps/ JSON 생성
        if inputMode == .newApp {
            print("   - 새 앱 등록: app-name-mapping.json 및 apps/ JSON 생성")
            updateAppNameMapping(name: finalAppName, nameEn: finalAppNameEn, folder: finalAppFolder)
            createAppModelJSON(name: finalAppName, nameEn: finalAppNameEn, folder: finalAppFolder)
        }

        // 저장 완료 확인
        verifyFileSaved(folder: finalAppFolder)

        showingSaveAlert = true
    }

    private func verifyFileSaved(folder: String) {
        // detailService를 통해 확인
        if let savedDetail = detailService.appDetails[folder] {
            print("✅ [AppDetailFormView] 파일 저장 확인:")
            print("   - appFolder: \(savedDetail.appFolder)")
            print("   - sourcePath: \(savedDetail.sourcePath)")
            print("   - 주요 기능: \(savedDetail.mainFeatures.count)개")
        } else {
            print("❌ [AppDetailFormView] 파일 저장 실패: \(folder)")
        }
    }

    private func getFolderName(for appName: String) -> String? {
        let fileManager = FileManager.default
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let mappingPath = documentsPath.appendingPathComponent("app-name-mapping.json")

        guard let data = try? Data(contentsOf: mappingPath),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let apps = json["apps"] as? [String: [String: String]],
              let appInfo = apps[appName],
              let folder = appInfo["folder"] else {
            return nil
        }

        return folder
    }

    private func updateAppNameMapping(name: String, nameEn: String, folder: String) {
        // app-name-mapping.json 파일 읽기 및 업데이트
        let fileManager = FileManager.default
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let mappingPath = documentsPath.appendingPathComponent("app-name-mapping.json")

        if let data = try? Data(contentsOf: mappingPath),
           var json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           var apps = json["apps"] as? [String: [String: String]] {

            // 새 앱 정보 추가
            apps[name] = [
                "nameEn": nameEn,
                "folder": folder,
                "bundleId": "com.leeo.\(folder.replacingOccurrences(of: "-", with: ""))"
            ]

            json["apps"] = apps

            // 저장
            if let updatedData = try? JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys]) {
                try? updatedData.write(to: mappingPath)
                print("✅ [AppDetailFormView] app-name-mapping.json 업데이트: \(name)")
            }
        }
    }

    private func createAppModelJSON(name: String, nameEn: String, folder: String) {
        // apps/ 폴더에 AppModel 형식의 JSON 생성
        let fileManager = FileManager.default
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let appsPath = documentsPath.appendingPathComponent("apps")

        // apps 디렉토리 생성
        if !fileManager.fileExists(atPath: appsPath.path) {
            try? fileManager.createDirectory(at: appsPath, withIntermediateDirectories: true)
        }

        let filePath = appsPath.appendingPathComponent("\(folder).json")
        let bundleId = "com.leeo.\(folder.replacingOccurrences(of: "-", with: ""))"

        // 기본 AppModel 데이터 생성
        let appModelData: [String: Any] = [
            "name": name,
            "nameEn": nameEn,
            "bundleId": bundleId,
            "currentVersion": "1.0.0",
            "status": "planning",
            "priority": "medium",
            "stats": [
                "totalTasks": 0,
                "done": 0,
                "inProgress": 0,
                "notStarted": 0
            ],
            "nextTasks": [],
            "allTasks": [],
            "notes": description.isEmpty ? nil : description
        ]

        // JSON 저장
        if let jsonData = try? JSONSerialization.data(withJSONObject: appModelData, options: [.prettyPrinted, .sortedKeys]) {
            try? jsonData.write(to: filePath)
            print("✅ [AppDetailFormView] apps/\(folder).json 생성 완료")
        }
    }

    private func clearForm() {
        selectedApp = nil
        appName = ""
        appNameEn = ""
        appFolder = ""
        sourcePath = ""
        description = ""
        mainFeatures = []
        ui = "SwiftUI"
        dataStorage = ""
        platforms = ["iOS"]
        hasWidget = false
        hasWatchApp = false
        hasKeyboard = false
        otherFrameworks = []
        constraints = []
        notes = ""
        isEditingExistingData = false
    }
}

#Preview {
    AppDetailFormView()
        .environmentObject(AppDetailService.shared)
        .environmentObject(PortfolioService.shared)
}

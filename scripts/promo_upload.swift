// 프로모션 텍스트를 나가 있는 버전(과 편집 중인 버전)에 바로 올린다. 심사 없이 바뀌는 유일한 칸.
// 사용: swift promo_upload.swift <promo.json> [--dry-run]
import Foundation
import CryptoKit

let args = CommandLine.arguments
let dryRun = args.contains("--dry-run")
let env: [String: String] = {
    let text = (try? String(contentsOfFile: NSString(string: "~/Documents/workspace/fastlane-shared/asc.env").expandingTildeInPath, encoding: .utf8)) ?? ""
    var out: [String: String] = [:]
    for line in text.split(separator: "\n") where !line.hasPrefix("#") {
        let parts = line.split(separator: "=", maxSplits: 1).map(String.init)
        if parts.count == 2 { out[parts[0]] = parts[1].trimmingCharacters(in: CharacterSet(charactersIn: "\" ")) }
    }
    return out
}()

func b64(_ d: Data) -> String {
    d.base64EncodedString().replacingOccurrences(of: "+", with: "-").replacingOccurrences(of: "/", with: "_").replacingOccurrences(of: "=", with: "")
}
func token() throws -> String {
    let path = NSString(string: env["ASC_KEY_PATH"]!).expandingTildeInPath
    let pem = try String(contentsOfFile: path, encoding: .utf8)
    let key = try P256.Signing.PrivateKey(pemRepresentation: pem)
    let header = b64(try JSONSerialization.data(withJSONObject: ["alg": "ES256", "kid": env["ASC_KEY_ID"]!, "typ": "JWT"]))
    let now = Int(Date().timeIntervalSince1970)
    let payload = b64(try JSONSerialization.data(withJSONObject: ["iss": env["ASC_ISSUER_ID"]!, "iat": now, "exp": now + 1000, "aud": "appstoreconnect-v1"]))
    let sig = try key.signature(for: Data("\(header).\(payload)".utf8)).rawRepresentation
    return "\(header).\(payload).\(b64(sig))"
}
let jwt = try token()

func call(_ method: String, _ path: String, _ body: [String: Any]? = nil) throws -> [String: Any] {
    var req = URLRequest(url: URL(string: "https://api.appstoreconnect.apple.com/" + path)!)
    req.httpMethod = method
    req.setValue("Bearer \(jwt)", forHTTPHeaderField: "Authorization")
    if let body {
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try JSONSerialization.data(withJSONObject: body)
    }
    let sem = DispatchSemaphore(value: 0)
    var result: (Data?, Int) = (nil, 0)
    URLSession.shared.dataTask(with: req) { d, r, _ in result = (d, (r as? HTTPURLResponse)?.statusCode ?? 0); sem.signal() }.resume()
    sem.wait()
    let json = (try? JSONSerialization.jsonObject(with: result.0 ?? Data())) as? [String: Any] ?? [:]
    guard (200..<300).contains(result.1) else {
        throw NSError(domain: "ASC", code: result.1, userInfo: [NSLocalizedDescriptionKey: "\(result.1) \(path): \(String(data: result.0 ?? Data(), encoding: .utf8)?.prefix(300) ?? "")"])
    }
    return json
}
func data(_ j: [String: Any]) -> [[String: Any]] { j["data"] as? [[String: Any]] ?? [] }
func attr(_ r: [String: Any], _ k: String) -> String? { (r["attributes"] as? [String: Any])?[k] as? String }

/// 레포 절 이름(de, nb, en …)을 스토어 로케일로.
func match(_ code: String, in available: [String]) -> String? {
    if available.contains(code) { return code }
    let map = ["en": "en-US", "de": "de-DE", "fr": "fr-FR", "es": "es-ES", "nl": "nl-NL", "nb": "no", "pt": "pt-BR"]
    if let m = map[code], available.contains(m) { return m }
    let lang = code.split(separator: "-").first.map(String.init) ?? code
    return available.first { $0.split(separator: "-").first.map(String.init) == lang }
}

let input = try JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: args[1]))) as! [String: [String: String]]
let liveStates: Set<String> = ["READY_FOR_SALE", "READY_FOR_DISTRIBUTION"]
let editable: Set<String> = ["WAITING_FOR_REVIEW", "IN_REVIEW", "PENDING_DEVELOPER_RELEASE", "PENDING_APPLE_RELEASE", "PREPARE_FOR_SUBMISSION", "DEVELOPER_REJECTED", "REJECTED", "METADATA_REJECTED", "INVALID_BINARY"]

for (bundle, texts) in input.sorted(by: { $0.key < $1.key }) {
    do {
        guard let app = data(try call("GET", "v1/apps?filter[bundleId]=\(bundle)")).first, let appID = app["id"] as? String else {
            print("❌ \(bundle): 앱 없음"); continue
        }
        let versions = data(try call("GET", "v1/apps/\(appID)/appStoreVersions?fields[appStoreVersions]=versionString,appStoreState,platform,createdDate&limit=50"))
        // 플랫폼마다 가장 새 나가 있는 버전 하나와 가장 새 편집 중인 버전 하나(다음 출시 때 문구가 되돌아가지 않게).
        let sorted = versions.sorted { (attr($0, "createdDate") ?? "") > (attr($1, "createdDate") ?? "") }
        var targets: [[String: Any]] = []
        for platform in Set(sorted.compactMap { attr($0, "platform") }) {
            let mine = sorted.filter { attr($0, "platform") == platform }
            let live = mine.first(where: { liveStates.contains(attr($0, "appStoreState") ?? "") })
            if let live { targets.append(live) }
            if let draft = mine.first(where: { editable.contains(attr($0, "appStoreState") ?? "") }),
               (attr(draft, "createdDate") ?? "") > (live.flatMap { attr($0, "createdDate") } ?? "") { targets.append(draft) }
        }
        if targets.isEmpty { print("❌ \(bundle): 나가 있거나 고칠 수 있는 버전 없음"); continue }
        for v in targets {
            let vid = v["id"] as! String
            let label = "\(attr(v, "platform") ?? "") \(attr(v, "versionString") ?? "") \(attr(v, "appStoreState") ?? "")"
            let locs = data(try call("GET", "v1/appStoreVersions/\(vid)/appStoreVersionLocalizations?fields[appStoreVersionLocalizations]=locale,promotionalText&limit=50"))
            let byLocale = Dictionary(uniqueKeysWithValues: locs.compactMap { l in attr(l, "locale").map { ($0, l) } })
            var done = 0, same = 0, missing: [String] = []
            for (code, text) in texts {
                guard text.count <= 170 else { print("  ⚠️ \(bundle) \(code) 170자 넘음 — 건너뜀"); continue }
                guard let locale = match(code, in: Array(byLocale.keys)), let l = byLocale[locale] else { missing.append(code); continue }
                if attr(l, "promotionalText") == text { same += 1; continue }
                if !dryRun {
                    _ = try call("PATCH", "v1/appStoreVersionLocalizations/\(l["id"] as! String)",
                                 ["data": ["type": "appStoreVersionLocalizations", "id": l["id"] as! String,
                                           "attributes": ["promotionalText": text]]])
                }
                done += 1
            }
            print("✅ \(bundle) [\(label)] \(dryRun ? "바꿀 것" : "바꿈") \(done) · 같음 \(same)\(missing.isEmpty ? "" : " · 스토어에 없는 언어 \(missing.sorted().joined(separator: ","))")")
        }
    } catch {
        print("❌ \(bundle): \(error.localizedDescription)")
    }
}

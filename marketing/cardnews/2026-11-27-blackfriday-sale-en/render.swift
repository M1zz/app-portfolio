// Black Friday sale cards (3 x 1080x1350): cover, apps, how to get it.
import SwiftUI
import AppKit
import UniformTypeIdentifiers

let W: CGFloat = 1080, H: CGFloat = 1350
let night = Color(red: 0.05, green: 0.05, blue: 0.08)
let dim = Color(red: 0.70, green: 0.72, blue: 0.80)
let gold = Color(red: 0.98, green: 0.75, blue: 0.20)
let coral = Color(red: 0.96, green: 0.36, blue: 0.40)
let iconDir = CommandLine.arguments[1]
let outDir = CommandLine.arguments[2]

struct App { let id: String; let name: String; let line: String }
let apps = [
    App(id: "com.Ysoup.TokenMemo", name: "Clip Keyboard", line: "Saved snippets and copied text, one tap from any keyboard"),
    App(id: "com.devkoan.StaffSinger", name: "StaffSinger", line: "Say do re mi to a metronome, get notes on a staff"),
    App(id: "com.leeo.HandsFreeMetronome", name: "Not My Tempo", line: "A metronome you control by voice: \"faster\", \"tempo 120\""),
    App(id: "com.leeo.LullabyRecipe", name: "Dalbit", line: "Layer rain, water drops and birdsong into your sleep sound"),
    App(id: "com.leeo.PixelMe", name: "Hantam", line: "Photo to bead pattern with real Perler, Hama and DMC counts"),
    App(id: "com.leeo.sunflower", name: "Sunny Sunflower", line: "Counts your minutes of real daylight on its own"),
    App(id: "com.Ysoup.CoolTime", name: "CoolTime", line: "A cooldown timer before impulse buys. Fitting this week"),
]

func icon(_ id: String) -> NSImage { NSImage(contentsOfFile: "\(iconDir)/\(id).jpg")! }

struct Bg: View {
    var body: some View {
        ZStack {
            night
            RadialGradient(colors: [gold.opacity(0.45), .clear], center: .topTrailing, startRadius: 0, endRadius: 760)
            RadialGradient(colors: [coral.opacity(0.35), .clear], center: .bottomLeading, startRadius: 0, endRadius: 760)
        }
    }
}

struct Top: View {
    let index: Int
    var body: some View {
        HStack {
            Text("Leeo · indie iOS apps").font(.system(size: 30, weight: .bold)).foregroundStyle(.white.opacity(0.85))
            Spacer()
            HStack(spacing: 10) {
                ForEach(0..<3) { i in Capsule().fill(.white.opacity(i == index ? 1 : 0.3)).frame(width: i == index ? 36 : 12, height: 12) }
            }
        }
    }
}

struct IconImg: View {
    let id: String; var size: CGFloat
    var body: some View {
        Image(nsImage: icon(id)).resizable().frame(width: size, height: size)
            .clipShape(RoundedRectangle(cornerRadius: size * 0.225, style: .continuous))
            .shadow(color: .black.opacity(0.4), radius: 16, y: 8)
    }
}

struct Cover: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Top(index: 0)
            Text("BLACK FRIDAY").font(.system(size: 44, weight: .black)).tracking(6).foregroundStyle(gold).padding(.top, 90)
            Text("Up to 80% off\nmy apps").font(.system(size: 128, weight: .black)).tracking(-3).lineSpacing(0)
                .foregroundStyle(.white).fixedSize(horizontal: false, vertical: true).padding(.top, 18)
            Text("Nov 27 to Dec 4").font(.system(size: 52, weight: .bold)).foregroundStyle(.white.opacity(0.9)).padding(.top, 28)
            Text("Your first subscription to each app.\n33 apps, all made by one indie developer.")
                .font(.system(size: 34, weight: .medium)).lineSpacing(8).foregroundStyle(dim).padding(.top, 22)
            Spacer()
            HStack(spacing: -26) {
                ForEach(Array(apps.enumerated()), id: \.offset) { i, a in
                    IconImg(id: a.id, size: 150).rotationEffect(.degrees(Double(i - 3) * 4))
                }
            }.frame(maxWidth: .infinity)
            Spacer().frame(height: 90)
        }.padding(.horizontal, 80).padding(.top, 64).frame(width: W, height: H, alignment: .topLeading).background(Bg()).clipped()
    }
}

struct Apps: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Top(index: 1)
            Text("A few of them").font(.system(size: 72, weight: .black)).tracking(-2).foregroundStyle(.white).padding(.top, 60)
            VStack(alignment: .leading, spacing: 30) {
                ForEach(apps, id: \.id) { a in
                    HStack(spacing: 28) {
                        IconImg(id: a.id, size: 104)
                        VStack(alignment: .leading, spacing: 6) {
                            Text(a.name).font(.system(size: 38, weight: .bold)).foregroundStyle(.white)
                            Text(a.line).font(.system(size: 28, weight: .medium)).foregroundStyle(dim)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                }
            }.padding(.top, 44)
            Spacer()
            Text("and 26 more").font(.system(size: 40, weight: .bold)).foregroundStyle(gold)
            Spacer().frame(height: 70)
        }.padding(.horizontal, 80).padding(.top, 64).frame(width: W, height: H, alignment: .topLeading).background(Bg()).clipped()
    }
}

struct HowTo: View {
    let steps = [
        ("Get or update the app", "Download it from the App Store, or update to the latest version."),
        ("Open it", "A Black Friday banner shows up once a day during the sale. Or go to Pro in the app."),
        ("Pick a plan", "The App Store payment sheet shows the discounted first period. Confirm."),
    ]
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Top(index: 2)
            Text("How to get it").font(.system(size: 96, weight: .black)).tracking(-2).foregroundStyle(.white).padding(.top, 80)
            VStack(alignment: .leading, spacing: 44) {
                ForEach(Array(steps.enumerated()), id: \.offset) { i, s in
                    HStack(alignment: .top, spacing: 30) {
                        Text("\(i + 1)").font(.system(size: 44, weight: .black)).foregroundStyle(night)
                            .frame(width: 76, height: 76).background(gold, in: Circle())
                        VStack(alignment: .leading, spacing: 10) {
                            Text(s.0).font(.system(size: 46, weight: .bold)).foregroundStyle(.white)
                            Text(s.1).font(.system(size: 32, weight: .medium)).lineSpacing(6).foregroundStyle(dim)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                }
            }.padding(.top, 64)
            Spacer()
            VStack(alignment: .leading, spacing: 14) {
                Text("For people subscribing to that app for the first time.")
                Text("Until Dec 4. After the first period it renews at the regular price. Cancel any time.")
            }.font(.system(size: 30, weight: .semibold)).lineSpacing(6).foregroundStyle(.white.opacity(0.9))
                .padding(36).frame(maxWidth: .infinity, alignment: .leading)
                .background(.white.opacity(0.1), in: RoundedRectangle(cornerRadius: 28, style: .continuous))
            Spacer().frame(height: 70)
        }.padding(.horizontal, 80).padding(.top, 64).frame(width: W, height: H, alignment: .topLeading).background(Bg()).clipped()
    }
}

@MainActor func save(_ v: some View, _ path: String) {
    let r = ImageRenderer(content: v); r.scale = 1
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.jpeg.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, r.cgImage!, [kCGImageDestinationLossyCompressionQuality: 0.92] as CFDictionary)
    CGImageDestinationFinalize(d); print(path)
}

@main struct Main {
    @MainActor static func main() {
        save(Cover(), "\(outDir)/01.jpg")
        save(Apps(), "\(outDir)/02.jpg")
        save(HowTo(), "\(outDir)/03.jpg")
    }
}

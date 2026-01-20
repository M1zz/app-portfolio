import SwiftUI

struct BriefingView: View {
    @EnvironmentObject var portfolio: PortfolioService

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text("CEO 일일 브리핑")
                    .font(.largeTitle)
                    .bold()

                Text("터미널에서 ./scripts/ceo-daily-briefing.sh를 실행하세요")
                    .foregroundColor(.secondary)

                Button("터미널에서 브리핑 생성") {
                    PortfolioService.shared.openInTerminal(script: "ceo-daily-briefing.sh")
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
    }
}

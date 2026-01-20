// SwiftUI View 템플릿

import SwiftUI

struct [Name]View: View {
    @StateObject private var viewModel = [Name]ViewModel()

    var body: some View {
        content
    }

    private var content: some View {
        VStack {
            // Content here
        }
    }
}

#Preview {
    [Name]View()
}

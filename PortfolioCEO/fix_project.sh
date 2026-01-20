#!/bin/bash
# project.pbxproj 파일 수정

PROJECT_FILE="PortfolioCEO.xcodeproj/project.pbxproj"

# 백업 생성
cp "$PROJECT_FILE" "${PROJECT_FILE}.backup"

# 타겟 Debug 설정 찾아서 필요한 설정 추가
perl -i -pe '
if (/581DB6802F1BE231004CDF8F \/\* Debug \*\/ = \{/) {
    $in_debug = 1;
}
if ($in_debug && /buildSettings = \{/) {
    $_ .= qq{				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
				CODE_SIGN_ENTITLEMENTS = PortfolioCEO/PortfolioCEO.entitlements;
				CODE_SIGN_STYLE = Automatic;
				COMBINE_HIDPI_IMAGES = YES;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_TEAM = "";
				ENABLE_HARDENED_RUNTIME = YES;
				ENABLE_PREVIEWS = YES;
				GENERATE_INFOPLIST_FILE = YES;
				INFOPLIST_KEY_LSApplicationCategoryType = "public.app-category.productivity";
				INFOPLIST_KEY_NSHumanReadableCopyright = "";
				INFOPLIST_KEY_NSUserNotificationUsageDescription = "일일 CEO 브리핑을 알려드립니다";
				INFOPLIST_KEY_NSAppleEventsUsageDescription = "터미널에서 스크립트를 실행합니다";
				LD_RUNPATH_SEARCH_PATHS = (
					"\$(inherited)",
					"\@executable_path/../Frameworks",
				);
				MARKETING_VERSION = 1.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.leeo.PortfolioCEO;
				PRODUCT_NAME = "\$(TARGET_NAME)";
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
};
    $in_debug = 0;
}
' "$PROJECT_FILE"

# 타겟 Release 설정 찾아서 필요한 설정 추가
perl -i -pe '
if (/581DB6812F1BE231004CDF8F \/\* Release \*\/ = \{/) {
    $in_release = 1;
}
if ($in_release && /buildSettings = \{/) {
    $_ .= qq{				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
				CODE_SIGN_ENTITLEMENTS = PortfolioCEO/PortfolioCEO.entitlements;
				CODE_SIGN_STYLE = Automatic;
				COMBINE_HIDPI_IMAGES = YES;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_TEAM = "";
				ENABLE_HARDENED_RUNTIME = YES;
				ENABLE_PREVIEWS = YES;
				GENERATE_INFOPLIST_FILE = YES;
				INFOPLIST_KEY_LSApplicationCategoryType = "public.app-category.productivity";
				INFOPLIST_KEY_NSHumanReadableCopyright = "";
				INFOPLIST_KEY_NSUserNotificationUsageDescription = "일일 CEO 브리핑을 알려드립니다";
				INFOPLIST_KEY_NSAppleEventsUsageDescription = "터미널에서 스크립트를 실행합니다";
				LD_RUNPATH_SEARCH_PATHS = (
					"\$(inherited)",
					"\@executable_path/../Frameworks",
				);
				MARKETING_VERSION = 1.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.leeo.PortfolioCEO;
				PRODUCT_NAME = "\$(TARGET_NAME)";
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
};
    $in_release = 0;
}
' "$PROJECT_FILE"

echo "✅ project.pbxproj 수정 완료"
echo "📝 백업: ${PROJECT_FILE}.backup"


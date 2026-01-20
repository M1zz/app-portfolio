#!/usr/bin/env python3
"""
Xcode 프로젝트 생성 스크립트 v2
모든 필수 빌드 설정 포함
"""

import os
import uuid
from pathlib import Path

def generate_uuid():
    """24자리 Xcode UUID 생성"""
    return uuid.uuid4().hex[:24].upper()

# Generate all UUIDs upfront
uuids = {
    'project': generate_uuid(),
    'main_group': generate_uuid(),
    'products_group': generate_uuid(),
    'app_target': generate_uuid(),
    'app_product': generate_uuid(),
    'sources_build_phase': generate_uuid(),
    'resources_build_phase': generate_uuid(),
    'frameworks_build_phase': generate_uuid(),
    'build_config_debug_project': generate_uuid(),
    'build_config_release_project': generate_uuid(),
    'build_config_debug_target': generate_uuid(),
    'build_config_release_target': generate_uuid(),
    'config_list_project': generate_uuid(),
    'config_list_target': generate_uuid(),
    'portfolioceo_group': generate_uuid(),
    'models_group': generate_uuid(),
    'views_group': generate_uuid(),
    'services_group': generate_uuid(),
    'resources_group': generate_uuid(),
    'app_swift': generate_uuid(),
    'content_view': generate_uuid(),
    'app_model': generate_uuid(),
    'portfolio': generate_uuid(),
    'dashboard_view': generate_uuid(),
    'briefing_view': generate_uuid(),
    'apps_grid_view': generate_uuid(),
    'project_detail_view': generate_uuid(),
    'decision_center_view': generate_uuid(),
    'quick_search_view': generate_uuid(),
    'settings_view': generate_uuid(),
    'portfolio_service': generate_uuid(),
    'notification_service': generate_uuid(),
    'decision_queue_service': generate_uuid(),
    'request_queue_service': generate_uuid(),
    'assets': generate_uuid(),
    'entitlements': generate_uuid(),
    'build_app_swift': generate_uuid(),
    'build_content_view': generate_uuid(),
    'build_app_model': generate_uuid(),
    'build_portfolio': generate_uuid(),
    'build_dashboard_view': generate_uuid(),
    'build_briefing_view': generate_uuid(),
    'build_apps_grid_view': generate_uuid(),
    'build_project_detail_view': generate_uuid(),
    'build_decision_center_view': generate_uuid(),
    'build_quick_search_view': generate_uuid(),
    'build_settings_view': generate_uuid(),
    'build_portfolio_service': generate_uuid(),
    'build_notification_service': generate_uuid(),
    'build_decision_queue_service': generate_uuid(),
    'build_request_queue_service': generate_uuid(),
    'build_assets': generate_uuid(),
}

def create_project_content():
    """Complete project.pbxproj content"""
    return f"""// !$*UTF8*$!
{{
	archiveVersion = 1;
	classes = {{
	}};
	objectVersion = 56;
	objects = {{

/* Begin PBXBuildFile section */
		{uuids['build_app_swift']} /* PortfolioCEOApp.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['app_swift']} /* PortfolioCEOApp.swift */; }};
		{uuids['build_content_view']} /* ContentView.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['content_view']} /* ContentView.swift */; }};
		{uuids['build_app_model']} /* AppModel.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['app_model']} /* AppModel.swift */; }};
		{uuids['build_portfolio']} /* Portfolio.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['portfolio']} /* Portfolio.swift */; }};
		{uuids['build_dashboard_view']} /* DashboardView.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['dashboard_view']} /* DashboardView.swift */; }};
		{uuids['build_briefing_view']} /* BriefingView.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['briefing_view']} /* BriefingView.swift */; }};
		{uuids['build_apps_grid_view']} /* AppsGridView.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['apps_grid_view']} /* AppsGridView.swift */; }};
		{uuids['build_project_detail_view']} /* ProjectDetailView.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['project_detail_view']} /* ProjectDetailView.swift */; }};
		{uuids['build_decision_center_view']} /* DecisionCenterView.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['decision_center_view']} /* DecisionCenterView.swift */; }};
		{uuids['build_quick_search_view']} /* QuickSearchView.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['quick_search_view']} /* QuickSearchView.swift */; }};
		{uuids['build_settings_view']} /* SettingsView.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['settings_view']} /* SettingsView.swift */; }};
		{uuids['build_portfolio_service']} /* PortfolioService.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['portfolio_service']} /* PortfolioService.swift */; }};
		{uuids['build_notification_service']} /* NotificationService.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['notification_service']} /* NotificationService.swift */; }};
		{uuids['build_decision_queue_service']} /* DecisionQueueService.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['decision_queue_service']} /* DecisionQueueService.swift */; }};
		{uuids['build_request_queue_service']} /* RequestQueueService.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {uuids['request_queue_service']} /* RequestQueueService.swift */; }};
		{uuids['build_assets']} /* Assets.xcassets in Resources */ = {{isa = PBXBuildFile; fileRef = {uuids['assets']} /* Assets.xcassets */; }};
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
		{uuids['app_product']} /* PortfolioCEO.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = PortfolioCEO.app; sourceTree = BUILT_PRODUCTS_DIR; }};
		{uuids['app_swift']} /* PortfolioCEOApp.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = PortfolioCEOApp.swift; sourceTree = "<group>"; }};
		{uuids['content_view']} /* ContentView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = ContentView.swift; sourceTree = "<group>"; }};
		{uuids['app_model']} /* AppModel.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = AppModel.swift; sourceTree = "<group>"; }};
		{uuids['portfolio']} /* Portfolio.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = Portfolio.swift; sourceTree = "<group>"; }};
		{uuids['dashboard_view']} /* DashboardView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = DashboardView.swift; sourceTree = "<group>"; }};
		{uuids['briefing_view']} /* BriefingView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = BriefingView.swift; sourceTree = "<group>"; }};
		{uuids['apps_grid_view']} /* AppsGridView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = AppsGridView.swift; sourceTree = "<group>"; }};
		{uuids['project_detail_view']} /* ProjectDetailView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = ProjectDetailView.swift; sourceTree = "<group>"; }};
		{uuids['decision_center_view']} /* DecisionCenterView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = DecisionCenterView.swift; sourceTree = "<group>"; }};
		{uuids['quick_search_view']} /* QuickSearchView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = QuickSearchView.swift; sourceTree = "<group>"; }};
		{uuids['settings_view']} /* SettingsView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = SettingsView.swift; sourceTree = "<group>"; }};
		{uuids['portfolio_service']} /* PortfolioService.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = PortfolioService.swift; sourceTree = "<group>"; }};
		{uuids['notification_service']} /* NotificationService.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = NotificationService.swift; sourceTree = "<group>"; }};
		{uuids['decision_queue_service']} /* DecisionQueueService.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = DecisionQueueService.swift; sourceTree = "<group>"; }};
		{uuids['request_queue_service']} /* RequestQueueService.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = RequestQueueService.swift; sourceTree = "<group>"; }};
		{uuids['assets']} /* Assets.xcassets */ = {{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; }};
		{uuids['entitlements']} /* PortfolioCEO.entitlements */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.entitlements; path = PortfolioCEO.entitlements; sourceTree = "<group>"; }};
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
		{uuids['frameworks_build_phase']} /* Frameworks */ = {{
			isa = PBXFrameworksBuildPhase;
			buildActionMask = 2147483647;
			files = (
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
		{uuids['main_group']} = {{
			isa = PBXGroup;
			children = (
				{uuids['portfolioceo_group']} /* PortfolioCEO */,
				{uuids['products_group']} /* Products */,
			);
			sourceTree = "<group>";
		}};
		{uuids['products_group']} /* Products */ = {{
			isa = PBXGroup;
			children = (
				{uuids['app_product']} /* PortfolioCEO.app */,
			);
			name = Products;
			sourceTree = "<group>";
		}};
		{uuids['portfolioceo_group']} /* PortfolioCEO */ = {{
			isa = PBXGroup;
			children = (
				{uuids['app_swift']} /* PortfolioCEOApp.swift */,
				{uuids['content_view']} /* ContentView.swift */,
				{uuids['models_group']} /* Models */,
				{uuids['views_group']} /* Views */,
				{uuids['services_group']} /* Services */,
				{uuids['resources_group']} /* Resources */,
				{uuids['entitlements']} /* PortfolioCEO.entitlements */,
			);
			path = PortfolioCEO;
			sourceTree = "<group>";
		}};
		{uuids['models_group']} /* Models */ = {{
			isa = PBXGroup;
			children = (
				{uuids['app_model']} /* AppModel.swift */,
				{uuids['portfolio']} /* Portfolio.swift */,
			);
			path = Models;
			sourceTree = "<group>";
		}};
		{uuids['views_group']} /* Views */ = {{
			isa = PBXGroup;
			children = (
				{uuids['dashboard_view']} /* DashboardView.swift */,
				{uuids['briefing_view']} /* BriefingView.swift */,
				{uuids['apps_grid_view']} /* AppsGridView.swift */,
				{uuids['project_detail_view']} /* ProjectDetailView.swift */,
				{uuids['decision_center_view']} /* DecisionCenterView.swift */,
				{uuids['quick_search_view']} /* QuickSearchView.swift */,
				{uuids['settings_view']} /* SettingsView.swift */,
			);
			path = Views;
			sourceTree = "<group>";
		}};
		{uuids['services_group']} /* Services */ = {{
			isa = PBXGroup;
			children = (
				{uuids['portfolio_service']} /* PortfolioService.swift */,
				{uuids['notification_service']} /* NotificationService.swift */,
				{uuids['decision_queue_service']} /* DecisionQueueService.swift */,
				{uuids['request_queue_service']} /* RequestQueueService.swift */,
			);
			path = Services;
			sourceTree = "<group>";
		}};
		{uuids['resources_group']} /* Resources */ = {{
			isa = PBXGroup;
			children = (
				{uuids['assets']} /* Assets.xcassets */,
			);
			path = Resources;
			sourceTree = "<group>";
		}};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
		{uuids['app_target']} /* PortfolioCEO */ = {{
			isa = PBXNativeTarget;
			buildConfigurationList = {uuids['config_list_target']} /* Build configuration list for PBXNativeTarget "PortfolioCEO" */;
			buildPhases = (
				{uuids['sources_build_phase']} /* Sources */,
				{uuids['frameworks_build_phase']} /* Frameworks */,
				{uuids['resources_build_phase']} /* Resources */,
			);
			buildRules = (
			);
			dependencies = (
			);
			name = PortfolioCEO;
			productName = PortfolioCEO;
			productReference = {uuids['app_product']} /* PortfolioCEO.app */;
			productType = "com.apple.product-type.application";
		}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
		{uuids['project']} /* Project object */ = {{
			isa = PBXProject;
			attributes = {{
				BuildIndependentTargetsInParallel = 1;
				LastSwiftUpdateCheck = 1500;
				LastUpgradeCheck = 1500;
				TargetAttributes = {{
					{uuids['app_target']} = {{
						CreatedOnToolsVersion = 15.0;
					}};
				}};
			}};
			buildConfigurationList = {uuids['config_list_project']} /* Build configuration list for PBXProject "PortfolioCEO" */;
			compatibilityVersion = "Xcode 14.0";
			developmentRegion = en;
			hasScannedForEncodings = 0;
			knownRegions = (
				en,
				Base,
			);
			mainGroup = {uuids['main_group']};
			productRefGroup = {uuids['products_group']} /* Products */;
			projectDirPath = "";
			projectRoot = "";
			targets = (
				{uuids['app_target']} /* PortfolioCEO */,
			);
		}};
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
		{uuids['resources_build_phase']} /* Resources */ = {{
			isa = PBXResourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				{uuids['build_assets']} /* Assets.xcassets in Resources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
		{uuids['sources_build_phase']} /* Sources */ = {{
			isa = PBXSourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				{uuids['build_app_swift']} /* PortfolioCEOApp.swift in Sources */,
				{uuids['build_content_view']} /* ContentView.swift in Sources */,
				{uuids['build_app_model']} /* AppModel.swift in Sources */,
				{uuids['build_portfolio']} /* Portfolio.swift in Sources */,
				{uuids['build_dashboard_view']} /* DashboardView.swift in Sources */,
				{uuids['build_briefing_view']} /* BriefingView.swift in Sources */,
				{uuids['build_apps_grid_view']} /* AppsGridView.swift in Sources */,
				{uuids['build_project_detail_view']} /* ProjectDetailView.swift in Sources */,
				{uuids['build_decision_center_view']} /* DecisionCenterView.swift in Sources */,
				{uuids['build_quick_search_view']} /* QuickSearchView.swift in Sources */,
				{uuids['build_settings_view']} /* SettingsView.swift in Sources */,
				{uuids['build_portfolio_service']} /* PortfolioService.swift in Sources */,
				{uuids['build_notification_service']} /* NotificationService.swift in Sources */,
				{uuids['build_decision_queue_service']} /* DecisionQueueService.swift in Sources */,
				{uuids['build_request_queue_service']} /* RequestQueueService.swift in Sources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
		{uuids['build_config_debug_project']} /* Debug */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ALWAYS_SEARCH_USER_PATHS = NO;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CLANG_ANALYZER_NONNULL = YES;
				CLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AGGRESSIVE;
				CLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CLANG_ENABLE_OBJC_WEAK = YES;
				CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
				CLANG_WARN_BOOL_CONVERSION = YES;
				CLANG_WARN_COMMA = YES;
				CLANG_WARN_CONSTANT_CONVERSION = YES;
				CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
				CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
				CLANG_WARN_DOCUMENTATION_COMMENTS = YES;
				CLANG_WARN_EMPTY_BODY = YES;
				CLANG_WARN_ENUM_CONVERSION = YES;
				CLANG_WARN_INFINITE_RECURSION = YES;
				CLANG_WARN_INT_CONVERSION = YES;
				CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
				CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
				CLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
				CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
				CLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
				CLANG_WARN_STRICT_PROTOTYPES = YES;
				CLANG_WARN_SUSPICIOUS_MOVE = YES;
				CLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
				CLANG_WARN_UNREACHABLE_CODE = YES;
				CLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = dwarf;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_TESTABILITY = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GCC_C_LANGUAGE_STANDARD = gnu17;
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_OPTIMIZATION_LEVEL = 0;
				GCC_PREPROCESSOR_DEFINITIONS = (
					"DEBUG=1",
					"$(inherited)",
				);
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNDECLARED_SELECTOR = YES;
				GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				LOCALIZATION_PREFERS_STRING_CATALOGS = YES;
				MACOSX_DEPLOYMENT_TARGET = 13.0;
				MTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
				MTL_FAST_MATH = YES;
				ONLY_ACTIVE_ARCH = YES;
				SDKROOT = macosx;
				SWIFT_ACTIVE_COMPILATION_CONDITIONS = "DEBUG $(inherited)";
				SWIFT_OPTIMIZATION_LEVEL = "-Onone";
			}};
			name = Debug;
		}};
		{uuids['build_config_release_project']} /* Release */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ALWAYS_SEARCH_USER_PATHS = NO;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CLANG_ANALYZER_NONNULL = YES;
				CLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AGGRESSIVE;
				CLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CLANG_ENABLE_OBJC_WEAK = YES;
				CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
				CLANG_WARN_BOOL_CONVERSION = YES;
				CLANG_WARN_COMMA = YES;
				CLANG_WARN_CONSTANT_CONVERSION = YES;
				CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
				CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
				CLANG_WARN_DOCUMENTATION_COMMENTS = YES;
				CLANG_WARN_EMPTY_BODY = YES;
				CLANG_WARN_ENUM_CONVERSION = YES;
				CLANG_WARN_INFINITE_RECURSION = YES;
				CLANG_WARN_INT_CONVERSION = YES;
				CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
				CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
				CLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
				CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
				CLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
				CLANG_WARN_STRICT_PROTOTYPES = YES;
				CLANG_WARN_SUSPICIOUS_MOVE = YES;
				CLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
				CLANG_WARN_UNREACHABLE_CODE = YES;
				CLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				ENABLE_NS_ASSERTIONS = NO;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GCC_C_LANGUAGE_STANDARD = gnu17;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNDECLARED_SELECTOR = YES;
				GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				LOCALIZATION_PREFERS_STRING_CATALOGS = YES;
				MACOSX_DEPLOYMENT_TARGET = 13.0;
				MTL_ENABLE_DEBUG_INFO = NO;
				MTL_FAST_MATH = YES;
				SDKROOT = macosx;
				SWIFT_COMPILATION_MODE = wholemodule;
			}};
			name = Release;
		}};
		{uuids['build_config_debug_target']} /* Debug */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
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
					"$(inherited)",
					"@executable_path/../Frameworks",
				);
				MARKETING_VERSION = 1.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.leeo.PortfolioCEO;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
			}};
			name = Debug;
		}};
		{uuids['build_config_release_target']} /* Release */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
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
					"$(inherited)",
					"@executable_path/../Frameworks",
				);
				MARKETING_VERSION = 1.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.leeo.PortfolioCEO;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
			}};
			name = Release;
		}};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
		{uuids['config_list_project']} /* Build configuration list for PBXProject "PortfolioCEO" */ = {{
			isa = XCConfigurationList;
			buildConfigurations = (
				{uuids['build_config_debug_project']} /* Debug */,
				{uuids['build_config_release_project']} /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		}};
		{uuids['config_list_target']} /* Build configuration list for PBXNativeTarget "PortfolioCEO" */ = {{
			isa = XCConfigurationList;
			buildConfigurations = (
				{uuids['build_config_debug_target']} /* Debug */,
				{uuids['build_config_release_target']} /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		}};
/* End XCConfigurationList section */
	}};
	rootObject = {uuids['project']} /* Project object */;
}}
"""

def main():
    print("🔨 Xcode 프로젝트 재생성 중...")

    # Create .xcodeproj directory
    xcodeproj_dir = Path("PortfolioCEO.xcodeproj")
    xcodeproj_dir.mkdir(exist_ok=True)

    # Generate and write project.pbxproj
    pbxproj_content = create_project_content()
    pbxproj_path = xcodeproj_dir / "project.pbxproj"

    with open(pbxproj_path, 'w') as f:
        f.write(pbxproj_content)

    print(f"✅ 프로젝트 파일 생성: {pbxproj_path}")
    print("✅ SWIFT_VERSION = 5.0 설정 완료")
    print("✅ GENERATE_INFOPLIST_FILE = YES 설정 완료")
    print("✅ 모든 빌드 설정 포함")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
폴더 구조를 반영한 제대로 된 Xcode 프로젝트 생성
"""

import os
import uuid
from pathlib import Path
from collections import defaultdict

def generate_uuid():
    return uuid.uuid4().hex[:24].upper()

def find_all_swift_files(base_path):
    swift_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.swift'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_path)
                swift_files.append(rel_path)
    return sorted(swift_files)

def organize_files_by_folder(swift_files):
    """파일들을 폴더별로 그룹화"""
    structure = defaultdict(list)
    for f in swift_files:
        dir_path = os.path.dirname(f)
        if dir_path == '':
            dir_path = 'root'
        structure[dir_path].append(f)
    return structure

# UUID 생성
project_uuid = generate_uuid()
main_group = generate_uuid()
products_group = generate_uuid()
app_target = generate_uuid()
app_product = generate_uuid()
sources_phase = generate_uuid()
resources_phase = generate_uuid()
frameworks_phase = generate_uuid()
debug_project = generate_uuid()
release_project = generate_uuid()
debug_target = generate_uuid()
release_target = generate_uuid()
config_list_project = generate_uuid()
config_list_target = generate_uuid()
assets_uuid = generate_uuid()
build_assets_uuid = generate_uuid()
entitlements_uuid = generate_uuid()

swift_files = find_all_swift_files("PortfolioCEO")
print(f"Found {len(swift_files)} Swift files")

file_structure = organize_files_by_folder(swift_files)
print(f"\nFolder structure:")
for folder in sorted(file_structure.keys()):
    print(f"  {folder}: {len(file_structure[folder])} files")

# UUID for each file and folder group
file_uuids = {f: generate_uuid() for f in swift_files}
build_uuids = {f: generate_uuid() for f in swift_files}
group_uuids = {folder: generate_uuid() for folder in file_structure.keys() if folder != 'root'}

# Build files section
build_section = ""
for f in swift_files:
    basename = os.path.basename(f)
    build_section += f'\t\t{build_uuids[f]} /* {basename} in Sources */ = {{isa = PBXBuildFile; fileRef = {file_uuids[f]} /* {basename} */; }};\n'
build_section += f'\t\t{build_assets_uuid} /* Assets.xcassets in Resources */ = {{isa = PBXBuildFile; fileRef = {assets_uuid} /* Assets.xcassets */; }};\n'

# File references section
ref_section = f'\t\t{app_product} /* PortfolioCEO.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = PortfolioCEO.app; sourceTree = BUILT_PRODUCTS_DIR; }};\n'
for f in swift_files:
    basename = os.path.basename(f)
    ref_section += f'\t\t{file_uuids[f]} /* {basename} */ = {{isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; path = "{basename}"; sourceTree = "<group>"; }};\n'
ref_section += f'\t\t{assets_uuid} /* Assets.xcassets */ = {{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; }};\n'
ref_section += f'\t\t{entitlements_uuid} /* PortfolioCEO.entitlements */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.entitlements; path = PortfolioCEO.entitlements; sourceTree = "<group>"; }};\n'

# Create PBXGroup sections for each folder
group_sections = []

# Root level files in main group
root_children = []
if 'root' in file_structure:
    for f in sorted(file_structure['root']):
        basename = os.path.basename(f)
        root_children.append(f'\t\t\t\t{file_uuids[f]} /* {basename} */,')

# Add folder groups to main group
for folder in sorted([f for f in file_structure.keys() if f != 'root']):
    # Get top-level folder name
    top_folder = folder.split('/')[0]
    if top_folder not in [c.split('/')[0] for c in root_children]:
        folder_uuid = group_uuids.get(top_folder, group_uuids.get(folder, generate_uuid()))
        root_children.append(f'\t\t\t\t{folder_uuid} /* {top_folder} */,')

# Add resources and entitlements
root_children.append(f'\t\t\t\t{assets_uuid} /* Assets.xcassets */,')
root_children.append(f'\t\t\t\t{entitlements_uuid} /* PortfolioCEO.entitlements */,')
root_children.append(f'\t\t\t\t{products_group} /* Products */,')

# Deduplicate root_children
seen = set()
unique_root_children = []
for child in root_children:
    if child not in seen:
        seen.add(child)
        unique_root_children.append(child)
root_children = unique_root_children

# Create groups for each folder
folder_groups = {}
for folder in sorted([f for f in file_structure.keys() if f != 'root']):
    parts = folder.split('/')

    # Create group for each level
    for i in range(len(parts)):
        current_path = '/'.join(parts[:i+1])
        if current_path in folder_groups:
            continue

        # Determine children
        children = []
        current_folder_name = parts[i]

        # Add files in this exact folder
        if current_path in file_structure:
            for f in sorted(file_structure[current_path]):
                if os.path.dirname(f) == current_path:
                    basename = os.path.basename(f)
                    children.append(f'\t\t\t\t{file_uuids[f]} /* {basename} */,')

        # Add subfolders
        for subfolder in sorted([f for f in file_structure.keys() if f != 'root']):
            subfolder_parts = subfolder.split('/')
            if len(subfolder_parts) == i + 2 and '/'.join(subfolder_parts[:i+1]) == current_path:
                subfolder_name = subfolder_parts[i+1]
                subfolder_uuid = group_uuids.get(subfolder, generate_uuid())
                if subfolder_uuid not in [c.split()[0] for c in children]:
                    children.append(f'\t\t\t\t{subfolder_uuid} /* {subfolder_name} */,')

        group_uuid = group_uuids.get(current_path, generate_uuid())
        group_uuids[current_path] = group_uuid

        folder_groups[current_path] = f'''\t\t{group_uuid} /* {current_folder_name} */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
{chr(10).join(children)}
\t\t\t);
\t\t\tpath = {current_folder_name};
\t\t\tsourceTree = "<group>";
\t\t}};'''

# Main group
main_group_section = f'''\t\t{main_group} /* PortfolioCEO */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
{chr(10).join(root_children)}
\t\t\t);
\t\t\tpath = PortfolioCEO;
\t\t\tsourceTree = "<group>";
\t\t}};'''

# Products group
products_group_section = f'''\t\t{products_group} /* Products */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{app_product} /* PortfolioCEO.app */,
\t\t\t);
\t\t\tname = Products;
\t\t\tsourceTree = "<group>";
\t\t}};'''

# Combine all groups
all_groups = [main_group_section] + list(folder_groups.values()) + [products_group_section]
group_section = '\n'.join(all_groups)

# Sources build phase
sources_files = []
for f in swift_files:
    basename = os.path.basename(f)
    sources_files.append(f'\t\t\t\t{build_uuids[f]} /* {basename} in Sources */,')

project_content = f'''// !$*UTF8*$!
{{
\tarchiveVersion = 1;
\tclasses = {{
\t}};
\tobjectVersion = 56;
\tobjects = {{

/* Begin PBXBuildFile section */
{build_section}
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
{ref_section}
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
\t\t{frameworks_phase} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
{group_section}
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
\t\t{app_target} /* PortfolioCEO */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {config_list_target};
\t\t\tbuildPhases = (
\t\t\t\t{sources_phase},
\t\t\t\t{frameworks_phase},
\t\t\t\t{resources_phase},
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = PortfolioCEO;
\t\t\tproductName = PortfolioCEO;
\t\t\tproductReference = {app_product};
\t\t\tproductType = "com.apple.product-type.application";
\t\t}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
\t\t{project_uuid} = {{
\t\t\tisa = PBXProject;
\t\t\tattributes = {{
\t\t\t\tBuildIndependentTargetsInParallel = 1;
\t\t\t\tLastSwiftUpdateCheck = 1540;
\t\t\t}};
\t\t\tbuildConfigurationList = {config_list_project};
\t\t\tcompatibilityVersion = "Xcode 14.0";
\t\t\tdevelopmentRegion = en;
\t\t\thasScannedForEncodings = 0;
\t\t\tknownRegions = (en, Base);
\t\t\tmainGroup = {main_group};
\t\t\tproductRefGroup = {products_group};
\t\t\tprojectDirPath = "";
\t\t\tprojectRoot = "";
\t\t\ttargets = ({app_target});
\t\t}};
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
\t\t{resources_phase} = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{build_assets_uuid},
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
\t\t{sources_phase} = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
{chr(10).join(sources_files)}
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
\t\t{debug_project} = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;
\t\t\t\tCLANG_ANALYZER_NONNULL = YES;
\t\t\t\tCLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
\t\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;
\t\t\t\tCOPY_PHASE_STRIP = NO;
\t\t\t\tDEBUG_INFORMATION_FORMAT = dwarf;
\t\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;
\t\t\t\tENABLE_TESTABILITY = YES;
\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu17;
\t\t\t\tGCC_DYNAMIC_NO_PIC = NO;
\t\t\t\tGCC_NO_COMMON_BLOCKS = YES;
\t\t\t\tGCC_OPTIMIZATION_LEVEL = 0;
\t\t\t\tMACOSX_DEPLOYMENT_TARGET = 13.0;
\t\t\t\tMTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
\t\t\t\tMTL_FAST_MATH = YES;
\t\t\t\tONLY_ACTIVE_ARCH = YES;
\t\t\t\tSDKROOT = macosx;
\t\t\t\tSWIFT_ACTIVE_COMPILATION_CONDITIONS = "DEBUG $(inherited)";
\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = "-Onone";
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{release_project} = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;
\t\t\t\tCLANG_ANALYZER_NONNULL = YES;
\t\t\t\tCLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
\t\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;
\t\t\t\tCOPY_PHASE_STRIP = NO;
\t\t\t\tDEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
\t\t\t\tENABLE_NS_ASSERTIONS = NO;
\t\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;
\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu17;
\t\t\t\tGCC_NO_COMMON_BLOCKS = YES;
\t\t\t\tMACOSX_DEPLOYMENT_TARGET = 13.0;
\t\t\t\tMTL_ENABLE_DEBUG_INFO = NO;
\t\t\t\tMTL_FAST_MATH = YES;
\t\t\t\tSDKROOT = macosx;
\t\t\t\tSWIFT_COMPILATION_MODE = wholemodule;
\t\t\t}};
\t\t\tname = Release;
\t\t}};
\t\t{debug_target} = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
\t\t\t\tCODE_SIGN_ENTITLEMENTS = PortfolioCEO/PortfolioCEO.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCOMBINE_HIDPI_IMAGES = YES;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tDEVELOPMENT_TEAM = "";
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = "Portfolio CEO";
\t\t\t\tINFOPLIST_KEY_LSApplicationCategoryType = "public.app-category.developer-tools";
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/../Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.leeo.PortfolioCEO;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{release_target} = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
\t\t\t\tCODE_SIGN_ENTITLEMENTS = PortfolioCEO/PortfolioCEO.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCOMBINE_HIDPI_IMAGES = YES;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tDEVELOPMENT_TEAM = "";
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = "Portfolio CEO";
\t\t\t\tINFOPLIST_KEY_LSApplicationCategoryType = "public.app-category.developer-tools";
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/../Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.leeo.PortfolioCEO;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t}};
\t\t\tname = Release;
\t\t}};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
\t\t{config_list_project} = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = ({debug_project}, {release_project});
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
\t\t{config_list_target} = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = ({debug_target}, {release_target});
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
/* End XCConfigurationList section */
\t}};
\trootObject = {project_uuid};
}}
'''

os.makedirs("PortfolioCEO.xcodeproj", exist_ok=True)
with open("PortfolioCEO.xcodeproj/project.pbxproj", "w") as f:
    f.write(project_content)

print(f"\n✅ 제대로 된 Xcode 프로젝트 생성 완료!")
print(f"   - {len(swift_files)}개 파일 포함")
print(f"   - {len([f for f in file_structure.keys() if f != 'root'])}개 폴더 그룹")

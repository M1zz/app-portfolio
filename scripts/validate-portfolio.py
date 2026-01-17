#!/usr/bin/env python3
"""
포트폴리오 데이터 유효성 검증 스크립트
Git pre-commit hook으로 사용하거나 수동 실행 가능
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class PortfolioValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.root_dir = Path(__file__).parent.parent

    def validate(self) -> bool:
        """전체 검증 실행"""
        print("🔍 포트폴리오 데이터 검증 중...\n")

        # 1. JSON 파일 유효성 검사
        self.validate_json_files()

        # 2. 앱 데이터 일관성 검사
        self.validate_app_data()

        # 3. stats 동기화 검사
        self.validate_stats_sync()

        # 4. 필수 필드 검사
        self.validate_required_fields()

        # 결과 출력
        self.print_results()

        return len(self.errors) == 0

    def validate_json_files(self):
        """JSON 파일 형식 검증"""
        apps_dir = self.root_dir / "apps"

        for json_file in apps_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                self.errors.append(f"❌ {json_file.name}: JSON 파싱 오류 - {str(e)}")

    def validate_app_data(self):
        """앱 데이터 검증"""
        apps_dir = self.root_dir / "apps"

        for json_file in apps_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    app_data = json.load(f)

                app_name = app_data.get('name', json_file.name)

                # 상태 값 검증
                if app_data.get('status') not in ['active', 'planning', 'maintenance', 'archived']:
                    self.errors.append(f"❌ {app_name}: 잘못된 status 값")

                # 우선순위 값 검증
                if app_data.get('priority') not in ['high', 'medium', 'low']:
                    self.errors.append(f"❌ {app_name}: 잘못된 priority 값")

                # 버전 형식 검증
                version = app_data.get('currentVersion', '')
                if version and not self._is_valid_version(version):
                    self.warnings.append(f"⚠️  {app_name}: 버전 형식 확인 필요 ({version})")

            except Exception as e:
                self.errors.append(f"❌ {json_file.name}: 검증 오류 - {str(e)}")

    def validate_stats_sync(self):
        """stats와 allTasks 동기화 검증"""
        apps_dir = self.root_dir / "apps"

        for json_file in apps_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    app_data = json.load(f)

                app_name = app_data.get('name', json_file.name)
                stats = app_data.get('stats', {})
                all_tasks = app_data.get('allTasks', [])

                # 실제 카운트 계산
                actual_total = len(all_tasks)
                actual_done = sum(1 for t in all_tasks if t.get('status') == 'done')
                actual_in_progress = sum(1 for t in all_tasks if t.get('status') == 'in-progress')
                actual_not_started = sum(1 for t in all_tasks if t.get('status') == 'not-started')

                # stats와 비교
                if stats.get('totalTasks') != actual_total:
                    self.errors.append(
                        f"❌ {app_name}: totalTasks 불일치 "
                        f"(stats: {stats.get('totalTasks')}, actual: {actual_total})"
                    )

                if stats.get('done') != actual_done:
                    self.errors.append(
                        f"❌ {app_name}: done 불일치 "
                        f"(stats: {stats.get('done')}, actual: {actual_done})"
                    )

                if stats.get('inProgress') != actual_in_progress:
                    self.errors.append(
                        f"❌ {app_name}: inProgress 불일치 "
                        f"(stats: {stats.get('inProgress')}, actual: {actual_in_progress})"
                    )

                if stats.get('notStarted') != actual_not_started:
                    self.errors.append(
                        f"❌ {app_name}: notStarted 불일치 "
                        f"(stats: {stats.get('notStarted')}, actual: {actual_not_started})"
                    )

            except Exception as e:
                self.errors.append(f"❌ {json_file.name}: stats 검증 오류 - {str(e)}")

    def validate_required_fields(self):
        """필수 필드 존재 여부 검증"""
        required_fields = ['name', 'nameEn', 'bundleId', 'currentVersion',
                          'status', 'priority', 'stats', 'allTasks']

        apps_dir = self.root_dir / "apps"

        for json_file in apps_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    app_data = json.load(f)

                app_name = app_data.get('name', json_file.name)

                for field in required_fields:
                    if field not in app_data:
                        self.errors.append(f"❌ {app_name}: 필수 필드 누락 - {field}")

            except Exception as e:
                self.errors.append(f"❌ {json_file.name}: 필드 검증 오류 - {str(e)}")

    def _is_valid_version(self, version: str) -> bool:
        """버전 형식 검증 (x.y.z)"""
        parts = version.split('.')
        if len(parts) != 3:
            return False
        return all(part.isdigit() for part in parts)

    def print_results(self):
        """검증 결과 출력"""
        if self.errors:
            print("\n❌ 오류 발견:\n")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print("\n⚠️  경고:\n")
            for warning in self.warnings:
                print(f"  {warning}")

        if not self.errors and not self.warnings:
            print("✅ 모든 검증 통과!\n")
        elif not self.errors:
            print(f"\n✅ 오류 없음 (경고 {len(self.warnings)}개)\n")
        else:
            print(f"\n❌ 검증 실패: {len(self.errors)}개 오류, {len(self.warnings)}개 경고\n")

def main():
    validator = PortfolioValidator()
    success = validator.validate()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

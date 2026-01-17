#!/usr/bin/env python3
"""
시각적 대시보드 생성 스크립트
포트폴리오 데이터를 HTML 대시보드로 변환
"""

import json
from pathlib import Path
from datetime import datetime

class DashboardGenerator:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.apps_data = []
        self.summary_data = {}

    def load_data(self):
        """포트폴리오 데이터 로드"""
        # Summary 데이터 로드
        summary_file = self.root_dir / "portfolio-summary.json"
        with open(summary_file, 'r', encoding='utf-8') as f:
            self.summary_data = json.load(f)

        # 앱 데이터 로드
        apps_dir = self.root_dir / "apps"
        for json_file in sorted(apps_dir.glob("*.json")):
            with open(json_file, 'r', encoding='utf-8') as f:
                self.apps_data.append(json.load(f))

    def generate_html(self) -> str:
        """HTML 대시보드 생성"""
        overview = self.summary_data.get('overview', {})

        # 우선순위별 앱 분류
        high_priority_apps = [app for app in self.apps_data if app.get('priority') == 'high']
        active_apps = [app for app in self.apps_data if app.get('status') == 'active']

        # 진행률 계산
        total_tasks = overview.get('totalTasks', 0)
        total_done = overview.get('totalDone', 0)
        completion_rate = (total_done / total_tasks * 100) if total_tasks > 0 else 0

        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍎 Leeo's App Portfolio Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}

        header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
        }}

        header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-card h3 {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}

        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}

        .progress-bar {{
            background: #e0e0e0;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin-top: 10px;
        }}

        .progress-fill {{
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
            transition: width 0.5s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.8em;
            font-weight: bold;
        }}

        .apps-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}

        .apps-section h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}

        .app-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}

        .app-card {{
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s;
        }}

        .app-card:hover {{
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}

        .app-card.high {{
            border-left: 5px solid #ff6b6b;
        }}

        .app-card.active {{
            background: #f0f8ff;
        }}

        .app-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }}

        .app-name {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}

        .app-version {{
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
        }}

        .app-meta {{
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}

        .badge {{
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 600;
        }}

        .badge.status {{
            background: #e3f2fd;
            color: #1976d2;
        }}

        .badge.priority-high {{
            background: #ffebee;
            color: #c62828;
        }}

        .badge.priority-medium {{
            background: #fff3e0;
            color: #ef6c00;
        }}

        .badge.priority-low {{
            background: #f1f8e9;
            color: #558b2f;
        }}

        .app-progress {{
            margin: 15px 0;
        }}

        .app-progress-text {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}

        .mini-progress {{
            background: #e0e0e0;
            border-radius: 5px;
            height: 8px;
            overflow: hidden;
        }}

        .mini-progress-fill {{
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
        }}

        .next-tasks {{
            margin-top: 15px;
        }}

        .next-tasks h4 {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
        }}

        .next-tasks ul {{
            list-style: none;
        }}

        .next-tasks li {{
            padding: 5px 0;
            font-size: 0.85em;
            color: #555;
            padding-left: 15px;
            position: relative;
        }}

        .next-tasks li:before {{
            content: "▸";
            position: absolute;
            left: 0;
            color: #667eea;
        }}

        .timestamp {{
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🍎 Leeo's App Portfolio</h1>
            <p>23개 iOS 앱 통합 관리 대시보드</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>전체 앱</h3>
                <div class="value">{overview.get('active', 0) + overview.get('planning', 0)}</div>
                <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                    활성 {overview.get('active', 0)} / 기획 {overview.get('planning', 0)}
                </div>
            </div>

            <div class="stat-card">
                <h3>전체 태스크</h3>
                <div class="value">{total_tasks}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {completion_rate:.1f}%">
                        {completion_rate:.1f}%
                    </div>
                </div>
            </div>

            <div class="stat-card">
                <h3>완료</h3>
                <div class="value" style="color: #4caf50;">{total_done}</div>
                <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                    {total_tasks - total_done}개 남음
                </div>
            </div>

            <div class="stat-card">
                <h3>진행 중</h3>
                <div class="value" style="color: #ff9800;">{overview.get('totalInProgress', 0)}</div>
                <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                    대기 {overview.get('totalNotStarted', 0)}개
                </div>
            </div>

            <div class="stat-card">
                <h3>높은 우선순위</h3>
                <div class="value" style="color: #f44336;">{overview.get('highPriority', 0)}</div>
                <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                    집중 관리 필요
                </div>
            </div>
        </div>

        <div class="apps-section">
            <h2>🔥 우선순위 높은 앱 ({len(high_priority_apps)}개)</h2>
            <div class="app-grid">
"""

        # 우선순위 높은 앱 카드
        for app in high_priority_apps:
            stats = app.get('stats', {})
            total = stats.get('totalTasks', 0)
            done = stats.get('done', 0)
            progress = (done / total * 100) if total > 0 else 0

            status_emoji = {
                'active': '🟢',
                'planning': '🟡',
                'maintenance': '🔵',
                'archived': '⚫'
            }.get(app.get('status', ''), '')

            next_tasks = app.get('nextTasks', [])[:3]  # 최대 3개만

            html += f"""
                <div class="app-card high active">
                    <div class="app-header">
                        <div class="app-name">{status_emoji} {app.get('name', '')}</div>
                        <div class="app-version">v{app.get('currentVersion', '1.0.0')}</div>
                    </div>

                    <div class="app-meta">
                        <span class="badge status">{app.get('status', '')}</span>
                        <span class="badge priority-high">high priority</span>
                    </div>

                    <div class="app-progress">
                        <div class="app-progress-text">
                            {done}/{total} 완료 ({progress:.0f}%) •
                            진행중 {stats.get('inProgress', 0)}개
                        </div>
                        <div class="mini-progress">
                            <div class="mini-progress-fill" style="width: {progress}%"></div>
                        </div>
                    </div>

                    <div class="next-tasks">
                        <h4>📋 다음 할 일</h4>
                        <ul>
"""

            for task in next_tasks:
                html += f"                            <li>{task}</li>\n"

            if not next_tasks:
                html += "                            <li style='color: #999;'>태스크 없음</li>\n"

            html += """                        </ul>
                    </div>
                </div>
"""

        html += """
            </div>
        </div>

        <div class="apps-section">
            <h2>📱 전체 활성 앱 ({})개)</h2>
            <div class="app-grid">
""".format(len(active_apps))

        # 전체 활성 앱 (간략 버전)
        for app in active_apps:
            if app.get('priority') == 'high':
                continue  # 이미 위에 표시됨

            stats = app.get('stats', {})
            total = stats.get('totalTasks', 0)
            done = stats.get('done', 0)
            progress = (done / total * 100) if total > 0 else 0

            priority_class = f"priority-{app.get('priority', 'medium')}"

            html += f"""
                <div class="app-card">
                    <div class="app-header">
                        <div class="app-name">{app.get('name', '')}</div>
                        <div class="app-version">v{app.get('currentVersion', '1.0.0')}</div>
                    </div>

                    <div class="app-meta">
                        <span class="badge status">{app.get('status', '')}</span>
                        <span class="badge {priority_class}">{app.get('priority', '')}</span>
                    </div>

                    <div class="app-progress">
                        <div class="app-progress-text">{done}/{total} 완료 ({progress:.0f}%)</div>
                        <div class="mini-progress">
                            <div class="mini-progress-fill" style="width: {progress}%"></div>
                        </div>
                    </div>
                </div>
"""

        html += f"""
            </div>
        </div>

        <div class="timestamp">
            마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""

        return html

    def save_dashboard(self):
        """대시보드 HTML 파일 저장"""
        html = self.generate_html()
        output_file = self.root_dir / "dashboard" / "index.html"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ 대시보드 생성 완료: {output_file}")
        print(f"   브라우저로 열기: open {output_file}")

def main():
    print("📊 대시보드 생성 중...\n")

    generator = DashboardGenerator()
    generator.load_data()
    generator.save_dashboard()

if __name__ == "__main__":
    main()

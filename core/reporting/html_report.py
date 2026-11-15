"""
HTML Report Generator — converts Markdown assessment report to standalone HTML with styling.
"""

from core.reporting.markdown_report import markdown_report_generator
from core.models import Laboratory, Asset, Service, Finding, AttackPath, Validation, Evidence


class HTMLReportGenerator:
    """Renders assessment reports as clean standalone HTML documents."""

    def generate(
        self,
        lab: Laboratory,
        assets: list[Asset],
        services: list[Service],
        findings: list[Finding],
        paths: list[AttackPath],
        validations: list[Validation],
        evidence: list[Evidence],
    ) -> str:
        md_content = markdown_report_generator.generate(
            lab, assets, services, findings, paths, validations, evidence
        )

        # Simple HTML wrapper
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SentriX Report - {lab.name}</title>
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #1f2937;
    max-width: 900px;
    margin: 40px auto;
    padding: 0 20px;
}}
h1, h2, h3 {{ color: #111827; }}
h1 {{ border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
h2 {{ border-bottom: 1px solid #e5e7eb; padding-bottom: 6px; margin-top: 30px; }}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}}
th, td {{
    border: 1px solid #d1d5db;
    padding: 10px 14px;
    text-align: left;
}}
th {{ background-color: #f3f4f6; }}
code {{
    background-color: #f3f4f6;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.9em;
}}
pre {{
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    padding: 16px;
    border-radius: 6px;
    white-space: pre-wrap;
}}
</style>
</head>
<body>
<pre>{md_content}</pre>
</body>
</html>"""
        return html


html_report_generator = HTMLReportGenerator()

"""
Markdown Report Generator — compiles a comprehensive, evidence-first cybersecurity assessment report.
"""

from datetime import datetime, timezone
import json
from typing import Any

from core.models import Laboratory, Asset, Service, Finding, AttackPath, Validation, Evidence


class MarkdownReportGenerator:
    """Generates structured Markdown reports from assessment data."""

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
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Parse scope policy
        policy = {}
        if lab.scope_policy_json:
            try:
                policy = json.loads(lab.scope_policy_json)
            except Exception:
                pass

        lines = [
            f"# ChainBreak Security Risk-Path Assessment Report",
            f"",
            f"**Laboratory:** {lab.name}  ",
            f"**Lab ID:** `{lab.id}`  ",
            f"**Assessment Date:** {now}  ",
            f"**Report Classification:** Synthetic Lab Assessment — Safe Read-Only Simulation  ",
            f"",
            f"---",
            f"",
            f"## 1. Executive Summary",
            f"",
            f"This report details the multi-step security risk paths identified in **{lab.name}** using graph-based path reasoning. ",
            f"All findings and relationships are evaluated against verifiable evidence records. ",
            f"No intrusive penetration testing, exploits, or unauthorized operations were performed.",
            f"",
            f"- **Total Assets in Scope:** {len([a for a in assets if a.id in policy.get('allowed_asset_ids', [])])} / {len(assets)}",
            f"- **Identified Security Findings:** {len(findings)}",
            f"- **Synthesized Candidate Risk Paths:** {len(paths)}",
            f"- **Safe Validations Performed:** {len(validations)}",
            f"- **Supporting Evidence Records:** {len(evidence)}",
            f"",
            f"---",
            f"",
            f"## 2. Laboratory Scope & Authorization Policy",
            f"",
            f"- **Validation Enabled:** {'Yes' if policy.get('validation_enabled') else 'No'}",
            f"- **Allowed Asset Scope:** {', '.join([f'`{aid}`' for aid in policy.get('allowed_asset_ids', [])]) if policy.get('allowed_asset_ids') else 'None'}",
            f"- **Permitted Validation Categories:** {', '.join(policy.get('allowed_validation_categories', [])) if policy.get('allowed_validation_categories') else 'None'}",
            f"- **Enforced Prohibitions:** {', '.join(policy.get('prohibited_actions', [])) if policy.get('prohibited_actions') else 'Standard safe fail-closed'}",
            f"",
            f"---",
            f"",
            f"## 3. Asset & Service Inventory",
            f"",
            f"| Asset Name | Type | IP Address | Hostname | Services Exposed |",
            f"|---|---|---|---|---|",
        ]

        # Group services by asset
        svc_by_asset: dict[str, list[str]] = {}
        for s in services:
            svc_desc = f"{s.name}:{s.port}" if s.port else s.name
            svc_by_asset.setdefault(s.asset_id, []).append(svc_desc)

        for a in assets:
            svcs = ", ".join(svc_by_asset.get(a.id, ["None"]))
            ip = a.ip_address or "N/A"
            host = a.hostname or "N/A"
            lines.append(f"| {a.name} | `{a.asset_type}` | {ip} | {host} | {svcs} |")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 4. Security Findings",
            f"",
            f"| Severity | Title | Asset | Category | Status |",
            f"|---|---|---|---|---|",
        ])

        asset_name_map = {a.id: a.name for a in assets}
        for f in findings:
            aname = asset_name_map.get(f.asset_id, f.asset_id)
            lines.append(f"| **{f.severity.upper()}** | {f.title} | {aname} | `{f.category}` | `{f.status}` |")

        lines.extend([
            f"",
            f"### Detailed Remediation Guidance",
            f"",
        ])
        for f in findings:
            if f.remediation:
                lines.append(f"- **{f.title}** ({f.severity.upper()}): {f.remediation}")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 5. Candidate Risk Paths (Multi-Step Graph Analysis)",
            f"",
        ])

        if not paths:
            lines.append("No candidate paths discovered in this laboratory.")
        else:
            for i, p in enumerate(paths, 1):
                lines.extend([
                    f"### Path #{i}: {p.title}",
                    f"",
                    f"- **Status:** `{p.path_status.upper()}`",
                    f"- **Analysis Rationale:**  \n  {p.rationale or 'N/A'}",
                    f"- **Evidence & Confidence:**  \n  {p.confidence_rationale or 'N/A'}",
                    f"",
                ])

        lines.extend([
            f"---",
            f"",
            f"## 6. Safe Validation Results",
            f"",
            f"| Target Asset | Action Requested | Scope Decision | Validation Outcome | Details / Reason |",
            f"|---|---|---|---|---|",
        ])

        if not validations:
            lines.append("| None | None | None | None | No validation operations logged. |")
        else:
            for v in validations:
                target = asset_name_map.get(v.asset_id, v.asset_id)
                lines.append(f"| {target} | `{v.requested_action}` | `{v.scope_decision}` | **{v.result.upper()}** | {v.reason or 'N/A'} |")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 7. Uncertainty & Epistemological Boundaries",
            f"",
            f"1. **Distinction of States:**",
            f"   - **Observed:** Directly confirmed from uploaded scan or configuration records.",
            f"   - **Inferred:** Logically derived from topology or security policies.",
            f"   - **Candidate:** A modeled multi-step risk scenario based on graph connectivity.",
            f"   - **Confirmed:** Validated via isolated read-only verification of a specific condition.",
            f"2. **Limitations:**",
            f"   - A candidate graph path does NOT prove exploitability.",
            f"   - Zero offensive or destructive testing was conducted.",
            f"   - All findings reflect point-in-time configuration snapshots.",
            f"",
            f"---",
            f"",
            f"*(Generated by ChainBreak — Evidence-First Cybersecurity Analysis Agent)*",
        ])

        return "\n".join(lines)


markdown_report_generator = MarkdownReportGenerator()

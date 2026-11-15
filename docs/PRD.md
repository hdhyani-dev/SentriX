# Product Requirements Document (PRD) — ChainBreak

## 1. Product Overview
**ChainBreak** is an AI-assisted cybersecurity analysis platform that models laboratory assets, services, security weaknesses, permissions, and observed relationships as a directed graph. Its purpose is to uncover how multiple isolated findings may combine into a multi-step risk path within an explicitly authorized laboratory environment.

## 2. Target Users
- **Cybersecurity Students & Educators:** For understanding multi-stage threat modeling and security posture.
- **Security Assessment Analysts:** For moving beyond flat vulnerability lists to graph-correlated risk paths.
- **Lab Researchers:** For controlled, safe validation under strict scope boundaries.

## 3. Core Principles
1. **Evidence First:** Every node and relationship is backed by tangible evidence records or flagged as missing.
2. **Deterministic Core:** All graph algorithms, path reasoning, and policy controls are deterministic.
3. **Fail-Closed Scope:** Authorization requires explicit inclusion in asset allowlists and permitted action categories.
4. **Safe by Default:** Strictly read-only validation against static snapshots. No live exploits or intrusive scanning.
5. **Explainable AI:** AI serves only as an explanatory lens; never modifies policy, records, or claims unverified facts.

## 4. Key Functional Features
- **Laboratory Scope Management:** Explicit asset allowlists, prohibited action enforcement, fail-closed authorization.
- **Asset & Service Inventory:** Asset attributes, operating system metadata, port and protocol services.
- **Finding Management:** Categorized weaknesses with severity ratings and remediation guidance.
- **Graph Construction (NetworkX):** Nodes for assets, services, findings, permissions; typed edges with evidence tracking.
- **Candidate Path Discovery:** Deterministic sequence generation with uncertainty and missing-evidence evaluation.
- **Safe Validation Engine:** Read-only checks against prepared evidence and configuration files.
- **Comprehensive Reporting:** Markdown and standalone HTML export.
- **Minimal Working UI:** Streamlit interface for exploring all system components.

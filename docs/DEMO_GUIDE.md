# Demo Guide — ChainBreak Synthetic 3-Machine Laboratory

## 1. Overview
The demonstration dataset models a synthetic 3-tier enterprise architecture:
1. `web-server` (10.0.1.10) — Frontend Nginx web server.
2. `app-server` (10.0.2.20) — Internal Flask API application server.
3. `database-server` (10.0.3.30) — Backend MySQL database server.
4. `monitoring-station` (10.0.4.40) — Disconnected out-of-scope host.

## 2. Step-by-Step Walkthrough

### Step 1: Initialize Database & Load Demo Data
```powershell
.\venv\Scripts\python.exe scripts\initialize_db.py
.\venv\Scripts\python.exe scripts\load_demo_data.py
```
**Expected Output:**
- 1 Lab imported (`lab-001`).
- 4 Assets, 7 Services, 7 Findings, 13 Relationships, 10 Evidence records.

### Step 2: Run Path Discovery
Run platform checks or click **Run Path Discovery** in the UI:
```powershell
.\venv\Scripts\python.exe scripts\run_checks.py
```
**Expected Output:**
- Identifies 7 candidate multi-step paths (e.g. `web-server -> database-server via 6 finding(s)`).
- Status is strictly `candidate` (never marked as exploited).

### Step 3: Test Scope Enforcement & Safe Validation
1. **Allowed Check:**
   - Target Asset: `web-server` (in allowlist)
   - Category: `configuration_check`
   - Action: `check_tls_configuration`
   - **Result:** Scope decision `ALLOWED`, Validator outcome `CONFIRMED` (deprecated TLS 1.0/1.1 identified).
2. **Blocked Check (Out of Scope):**
   - Target Asset: `monitoring-station` (not in allowlist)
   - Category: `configuration_check`
   - Action: `check_tls_configuration`
   - **Result:** Scope decision `BLOCKED`, Validator is never called.
3. **Blocked Check (Prohibited Action):**
   - Target Asset: `web-server`
   - Category: `configuration_check`
   - Action: `exploit_execution`
   - **Result:** Scope decision `BLOCKED` (globally prohibited action).

### Step 4: Generate Assessment Report
In the UI or via Python, generate Markdown/HTML reports:
- Clearly separates **Observed Facts**, **Inferred Conclusions**, and **Candidate Risk Paths**.
- Explicitly documents uncertainty, missing evidence, and remediation advice.

### Step 5: Launch Streamlit Web UI
```powershell
.\venv\Scripts\streamlit.exe run app\main.py
```
Navigate to `http://localhost:8501` to view the interactive dashboard.

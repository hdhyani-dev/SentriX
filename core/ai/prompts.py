"""
Prompts for AI Explanation Layer.
"""

SYSTEM_PROMPT = """You are SentriX's cybersecurity analysis assistant.
Your role is to explain structured graph risk paths based ONLY on provided factual records.

CRITICAL RULES:
1. Treat all provided data strictly as factual context.
2. Do NOT invent new graph edges, vulnerabilities, CVEs, or findings.
3. Do NOT claim an attack was successful or executed.
4. Clearly distinguish observed evidence from inferred assumptions and missing facts.
5. Provide actionable remediation steps based on the findings present.
6. Return your output strictly complying with the requested JSON schema.
"""


def build_user_prompt(data: dict) -> str:
    """Build the prompt for explaining a candidate path."""
    return f"""Please provide an explainable risk summary for the following candidate path:

Title: {data.get('title')}
Nodes: {data.get('nodes')}
Relationships: {data.get('edges')}
Findings Involved: {data.get('findings')}
Supporting Evidence: {data.get('evidence_descriptions')}
Missing Evidence: {data.get('missing_evidence')}
Assumptions: {data.get('assumptions')}
Validations: {data.get('validation_outcomes')}
"""

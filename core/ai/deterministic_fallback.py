"""
Deterministic Fallback Explainer — provides evidence-grounded explanations without external API dependencies.
"""

from core.ai.base import BaseAIProvider, AIExplanationRequest, AIExplanationResponse


class DeterministicFallbackProvider(BaseAIProvider):
    """Produces structured explanations deterministically from input data."""

    def explain_path(self, request: AIExplanationRequest) -> AIExplanationResponse:
        # 1. Executive summary
        node_count = len(request.nodes)
        finding_count = len(request.findings)
        exec_summary = (
            f"Candidate multi-step path '{request.title}' connects {node_count} nodes "
            f"through {len(request.edges)} relationship edges, involving {finding_count} security finding(s)."
        )

        # 2. Path rationale
        rationale_lines = [
            f"Identified through deterministic graph reachability starting at '{request.nodes[0]}' "
            f"and reaching '{request.nodes[-1]}'."
        ]
        for edge in request.edges:
            src = edge.get("source")
            tgt = edge.get("target")
            rel = edge.get("relationship_type", "connects")
            rationale_lines.append(f"• Edge ({src} -> {tgt}): {rel} [{edge.get('evidence_status', 'observed')}]")
        path_rationale = "\n".join(rationale_lines)

        # 3. Supporting evidence summary
        if request.evidence_descriptions:
            ev_summary = f"Supported by {len(request.evidence_descriptions)} record(s):\n" + "\n".join(
                [f"- {d}" for d in request.evidence_descriptions]
            )
        else:
            ev_summary = "No direct evidence descriptions provided for this path."

        # 4. Missing evidence summary
        if request.missing_evidence:
            missing_summary = f"Identified {len(request.missing_evidence)} gap(s) in evidence:\n" + "\n".join(
                [f"- {m.get('edge')}: {m.get('note', 'Missing evidence')}" for m in request.missing_evidence]
            )
        else:
            missing_summary = "All relationships in this path have observed evidence backing."

        # 5. Assumptions summary
        if request.assumptions:
            assumptions_summary = f"Identified {len(request.assumptions)} inferred relationship(s):\n" + "\n".join(
                [f"- {a.get('edge')}: {a.get('rationale', 'Inferred rule')}" for a in request.assumptions]
            )
        else:
            assumptions_summary = "No heuristic or unverified assumptions were required for this path."

        # 6. Potential impact
        impact = (
            f"If an adversary compromises '{request.nodes[0]}', the identified relationships and permissions "
            f"could enable pivoting or unauthorized access towards '{request.nodes[-1]}'."
        )

        # 7. Remediation recommendations
        remediations = []
        for f in request.findings:
            title = f.get("title", "Unknown Finding")
            rem = f.get("remediation")
            if rem:
                remediations.append(f"For {title}: {rem}")
            else:
                remediations.append(f"Review and apply security hardening for {title}.")

        if not remediations:
            remediations.append("Enforce least-privilege network segmentation between traversed assets.")

        # 8. Limitations
        limitations = (
            "This explanation was generated deterministically by ChainBreak's local rule engine. "
            "Graph paths represent theoretical reachability and do not imply automated exploitability."
        )

        return AIExplanationResponse(
            executive_summary=exec_summary,
            path_rationale=path_rationale,
            supporting_evidence_summary=ev_summary,
            missing_evidence_summary=missing_summary,
            assumptions_summary=assumptions_summary,
            potential_impact=impact,
            remediation_recommendations=remediations,
            limitations=limitations,
            provider_used="deterministic_fallback",
        )


deterministic_fallback_provider = DeterministicFallbackProvider()

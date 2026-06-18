"""
Explanation Engine — Generate human-readable explanations from proof trees.
"""

from __future__ import annotations

from ..explain.proof import ProofTree, StepType


class Narrator:
    """
    Converts proof trees into natural language explanations.
    Tiered: one-liner → short → detailed.
    """

    @staticmethod
    def one_line(tree: ProofTree) -> str:
        """One-line summary."""
        result_map = {
            "PROVED": "Yes",
            "DISPROVED": "No",
            "UNKNOWN": "Unknown",
            "INCONSISTENT": "Inconsistent",
        }
        return result_map.get(tree.result, tree.result)

    @staticmethod
    def short(tree: ProofTree) -> str:
        """Short explanation for users."""
        if tree.result == "PROVED":
            return f"✅ Yes — {tree.steps[-1].justification if tree.steps else 'proved'}"
        elif tree.result == "DISPROVED":
            fails = [s for s in tree.steps if s.type == StepType.FAIL]
            if fails:
                return f"❌ No — failed to prove: {fails[-1].content}"
            return "❌ No"
        elif tree.result == "UNKNOWN":
            return "❓ Unknown — insufficient information"
        elif tree.result == "INCONSISTENT":
            return "⚠️ Inconsistent knowledge base — contradictions detected"
        return tree.result

    @staticmethod
    def medium(tree: ProofTree) -> str:
        """Medium explanation with rule trace."""
        lines = [f"Query: {tree.query}", f"Result: {tree.result}", ""]

        proved = [s for s in tree.steps if s.type == StepType.CONCLUDE]
        fired = [s for s in tree.steps if s.type == StepType.RULE]

        if fired:
            lines.append("Rules used:")
            for s in fired:
                lines.append(f"  • {s.justification}")

        if proved:
            lines.append(f"\nConclusion: {proved[-1].content}")
        else:
            fails = [s for s in tree.steps if s.type == StepType.FAIL]
            if fails:
                lines.append(f"\nCould not establish: {fails[-1].content}")

        return "\n".join(lines)

    @staticmethod
    def detailed(tree: ProofTree) -> str:
        """Full proof tree text."""
        return tree.to_text()

    @staticmethod
    def counterexample(tree: ProofTree) -> str:
        """Explain why something is false."""
        fails = [s for s in tree.steps if s.type == StepType.FAIL]
        if not fails:
            return "No counterexample available."

        lines = ["Why false:", ""]
        for f in fails:
            lines.append(f"  • Could not prove: {f.content}")
            if f.justification:
                lines.append(f"    Because: {f.justification}")

        return "\n".join(lines)

    @staticmethod
    def missing_premises(tree: ProofTree) -> str:
        """Explain what's needed to prove an unknown."""
        fails = [s for s in tree.steps if s.type == StepType.FAIL]
        if not fails:
            return "No missing premises identified."

        lines = ["To prove this, you would need:", ""]
        for f in fails:
            lines.append(f"  • {f.content}")

        return "\n".join(lines)

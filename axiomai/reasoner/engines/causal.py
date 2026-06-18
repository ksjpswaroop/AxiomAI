"""
Causal Reasoning — Causal graph reasoning with NetworkX.
"""

from __future__ import annotations

import networkx as nx


class CausalEngine:
    """
    Causal reasoning via directed graphs.

    Supports:
    - Causal chain explanation
    - Root cause analysis
    - Counterfactual simulation (what-if)
    - Intervention (do-calculus lite)
    """

    def __init__(self):
        self._graph = nx.DiGraph()

    def add_causal_edge(self, cause: str, effect: str, strength: float = 1.0):
        """Add a causal edge: cause → effect."""
        self._graph.add_edge(cause, effect, weight=strength)

    def add_causal_fact(self, cause: str, effect: str):
        """Add a causal relationship as a fact."""
        self._graph.add_edge(cause, effect, weight=1.0)

    def explain_chain(self, effect: str) -> list[str]:
        """Explain all causes leading to an effect (root causes)."""
        try:
            ancestors = nx.ancestors(self._graph, effect)
            return sorted(ancestors)
        except nx.NetworkXError:
            return []

    def root_causes(self, effect: str) -> list[str]:
        """Find root causes (nodes with no predecessors)."""
        ancestors = self.explain_chain(effect)
        roots = []
        for node in ancestors:
            if self._graph.in_degree(node) == 0:
                roots.append(node)
        return roots

    def trace_path(self, cause: str, effect: str) -> list[str] | None:
        """Find the path from cause to effect, if it exists."""
        try:
            path = nx.shortest_path(self._graph, cause, effect)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def all_paths(self, cause: str, effect: str) -> list[list[str]]:
        """Find all paths from cause to effect."""
        try:
            return list(nx.all_simple_paths(self._graph, cause, effect))
        except nx.NetworkXError:
            return []

    def simulate_whatif(self, node: str, new_value: bool) -> dict[str, bool]:
        """
        Counterfactual: what if a node had a different value?
        Returns affected downstream nodes.
        """
        affected = set()
        descendants = nx.descendants(self._graph, node)

        # Simple propagation: if cause changes, all descendants potentially change
        for desc in descendants:
            path = self.trace_path(node, desc)
            if path:
                affected.add(desc)

        return {n: new_value for n in affected}

    def intervention(self, node: str, value: bool) -> nx.DiGraph:
        """
        Do-calculus lite: force a node to a value, remove incoming edges.
        Returns a new causal graph with the intervention applied.
        """
        g2 = self._graph.copy()
        # Remove incoming edges to node (it's now externally set)
        for pred in list(g2.predecessors(node)):
            g2.remove_edge(pred, node)
        return g2

    def has_cycle(self) -> bool:
        """Check if the causal graph has cycles."""
        return not nx.is_directed_acyclic_graph(self._graph)

    def topological_order(self) -> list[str]:
        """Return nodes in topological order."""
        try:
            return list(nx.topological_sort(self._graph))
        except nx.NetworkXError:
            return []

    def to_dot(self, path: str):
        """Export causal graph to DOT format."""
        nx.drawing.nx_pydot.write_dot(self._graph, path)

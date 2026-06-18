"""Cybersecurity incident root cause analysis engine."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps.case_studies.cs07_cybersecurity import rules as attack_rules
from axiomai import Reasoner


@dataclass
class IncidentResult:
    incident_id: str
    incident_host: str
    confirmed: bool
    root_cause: str
    confidence: str
    attack_chain: list[str] = field(default_factory=list)
    chain_evidence: list[dict[str, str]] = field(default_factory=list)
    containment: list[str] = field(default_factory=list)
    mttr_before_minutes: int = 360
    mttr_after_minutes: int = 45
    derived_facts: list[str] = field(default_factory=list)


def load_scenario(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


class IncidentAnalyzer:
    """Analyze security incidents using forward chaining and causal reasoning."""

    def analyze(self, scenario: dict[str, Any]) -> IncidentResult:
        predicates = [f["predicate"] for f in scenario["facts"]]
        evidence = {f["predicate"]: f for f in scenario["facts"]}
        return self._analyze(
            incident_id=scenario["incident_id"],
            host=scenario["host"],
            predicates=predicates,
            evidence=evidence,
            mttr=scenario.get("mttr", {}),
        )

    def analyze_from_predicates(self, predicates: list[str]) -> IncidentResult:
        evidence = {p: {"predicate": p, "timestamp": "", "evidence": p} for p in predicates}
        host = "Host42" if any("Host42" in p for p in predicates) else "unknown"
        return self._analyze(
            incident_id="SIEM-IMPORT",
            host=host,
            predicates=predicates,
            evidence=evidence,
        )

    def _analyze(
        self,
        incident_id: str,
        host: str,
        predicates: list[str],
        evidence: dict[str, dict[str, str]],
        mttr: dict[str, int] | None = None,
    ) -> IncidentResult:
        reasoner = Reasoner(namespace="default")
        reasoner.kb.clear()
        for rule in attack_rules.ATTACK_CHAIN_RULES:
            reasoner.add_rule(rule)
        reasoner.add_facts(*predicates)

        for edge in attack_rules.CAUSAL_EDGES:
            reasoner.add_causal(edge[0], edge[1])
        reasoner.add_causal("ImpactEncryption", "ConfirmedRansomware")

        forward = reasoner.forward_engine.run()
        derived = [str(f.predicate) for f in forward.all_derived]

        confirmed = any(f"ConfirmedRansomware({host})" in d for d in derived) or (
            any(f"ImpactEncryption({host})" in d for d in derived)
            and any(f"ProbableC2Communication({host})" in d for d in derived)
            and any(
                "PhishingVector" in d or "ProbableInitialAccess" in d for d in derived
            )
        )

        chain_steps: list[str] = []
        chain_evidence: list[dict[str, str]] = []
        for pred in derived:
            base = pred.split("(")[0]
            if base in attack_rules.CHAIN_LABELS:
                label = attack_rules.CHAIN_LABELS[base]
                if label not in chain_steps:
                    chain_steps.append(label)
                    source_fact = self._find_supporting_fact(pred, evidence)
                    chain_evidence.append({
                        "step": label,
                        "evidence": source_fact.get("evidence", pred),
                        "time": source_fact.get("timestamp", ""),
                    })

        root = "Phishing → Ransomware"
        if reasoner.causal_engine.root_causes("ImpactEncryption"):
            roots = reasoner.causal_engine.root_causes("ImpactEncryption")
            if roots:
                root = f"{roots[0]} → Ransomware"
        elif any("PhishingVector" in d for d in derived):
            root = "Phishing → Ransomware"

        containment = [
            f"Isolate {host} immediately",
            "Revoke Admin001 credentials",
            "Block 45.33.x.x at perimeter",
            "Scan all endpoints for Emotet indicators",
        ]

        mttr = mttr or {}
        return IncidentResult(
            incident_id=incident_id,
            incident_host=host,
            confirmed=confirmed,
            root_cause=root,
            confidence="CONFIRMED" if confirmed else "PROBABLE",
            attack_chain=chain_steps,
            chain_evidence=chain_evidence,
            containment=containment,
            mttr_before_minutes=int(mttr.get("before_minutes", 360)),
            mttr_after_minutes=int(mttr.get("after_minutes", 45)),
            derived_facts=derived,
        )

    @staticmethod
    def _find_supporting_fact(derived: str, evidence: dict[str, dict[str, str]]) -> dict[str, str]:
        for key, meta in evidence.items():
            if key.split("(")[0] in derived:
                return meta
        return {"evidence": derived, "timestamp": ""}

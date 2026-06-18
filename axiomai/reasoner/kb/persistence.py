"""
SQLite-backed persistent knowledge base.
"""

from __future__ import annotations

import json
import uuid
from typing import Optional

from ..core.models import Fact, Predicate, Rule
from .schema import (
    ContradictionRow,
    FactRow,
    InferenceRunRow,
    ProofRow,
    RuleRow,
    create_session_factory,
)
from .store import ContradictionReport, KnowledgeBase


class PersistentKnowledgeBase(KnowledgeBase):
    """Knowledge base that persists facts and rules to SQLite."""

    def __init__(self, url: str, namespace: str = "default"):
        super().__init__(namespace=namespace)
        self._url = url
        self._Session = create_session_factory(url)
        self._load()

    def _load(self):
        session = self._Session()
        try:
            for row in session.query(FactRow).filter_by(namespace=self.namespace).all():
                pred_str = row.predicate
                negated = pred_str.startswith("¬")
                if negated:
                    pred_str = pred_str.lstrip("¬")
                metadata = json.loads(row.metadata_json) if row.metadata_json else {}
                if negated:
                    metadata["negated"] = True
                fact = Fact(
                    id=row.id,
                    predicate=Predicate.parse(pred_str),
                    source=row.source,
                    confidence_source=row.confidence_source,
                    valid_from=row.valid_from,
                    valid_to=row.valid_to,
                    metadata=metadata,
                )
                key = self._fact_key(fact.predicate, fact)
                self._facts[key] = fact
            for row in session.query(RuleRow).filter_by(namespace=self.namespace).all():
                rule = Rule.parse(row.rule_str, priority=row.priority)
                rule.id = row.id
                rule.enabled = row.enabled
                self._rules[rule.id] = rule
        finally:
            session.close()

    def add_fact(self, fact: Fact) -> Fact:
        result = super().add_fact(fact)
        session = self._Session()
        try:
            key = self._fact_key(fact.predicate, fact)
            row = session.get(FactRow, fact.id) or FactRow(id=fact.id)
            row.predicate = key
            row.namespace = self.namespace
            row.source = fact.source
            row.confidence_source = fact.confidence_source
            row.valid_from = fact.valid_from
            row.valid_to = fact.valid_to
            row.metadata_json = json.dumps(fact.metadata) if fact.metadata else None
            session.merge(row)
            session.commit()
        finally:
            session.close()
        return result

    def add_rule(self, rule: Rule) -> Rule:
        result = super().add_rule(rule)
        session = self._Session()
        try:
            row = session.get(RuleRow, rule.id) or RuleRow(id=rule.id)
            row.rule_str = str(rule)
            row.priority = rule.priority
            row.enabled = rule.enabled
            row.namespace = self.namespace
            session.merge(row)
            session.commit()
        finally:
            session.close()
        return result

    def retract_fact(self, predicate_str: str) -> bool:
        removed = super().retract_fact(predicate_str)
        if removed:
            session = self._Session()
            try:
                session.query(FactRow).filter_by(
                    predicate=predicate_str, namespace=self.namespace
                ).delete()
                session.commit()
            finally:
                session.close()
        return removed

    def retract_rule(self, rule_id: str) -> bool:
        removed = super().retract_rule(rule_id)
        if removed:
            session = self._Session()
            try:
                session.query(RuleRow).filter_by(id=rule_id).delete()
                session.commit()
            finally:
                session.close()
        return removed

    def clear(self):
        super().clear()
        session = self._Session()
        try:
            session.query(FactRow).filter_by(namespace=self.namespace).delete()
            session.query(RuleRow).filter_by(namespace=self.namespace).delete()
            session.commit()
        finally:
            session.close()

    def record_inference_run(
        self,
        query: str,
        mode: str,
        result: str,
        duration_ms: float,
        run_hash: str,
    ) -> str:
        """Persist an inference run for audit."""
        run_id = str(uuid.uuid4())
        session = self._Session()
        try:
            row = InferenceRunRow(
                id=run_id,
                query=query,
                mode=mode,
                result=result,
                duration_ms=duration_ms,
                kb_snapshot=self.snapshot(),
                run_hash=run_hash,
            )
            session.add(row)
            session.commit()
        finally:
            session.close()
        return run_id

    def record_proof(
        self,
        query: str,
        result: str,
        proof_json: str,
        run_hash: Optional[str] = None,
    ) -> str:
        """Persist a proof trace."""
        proof_id = str(uuid.uuid4())
        session = self._Session()
        try:
            row = ProofRow(
                id=proof_id,
                query=query,
                result=result,
                proof_json=proof_json,
                run_hash=run_hash,
            )
            session.add(row)
            session.commit()
        finally:
            session.close()
        return proof_id

    def list_proofs(
        self,
        query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Query persisted proof traces."""
        session = self._Session()
        try:
            q = session.query(ProofRow).order_by(ProofRow.created_at.desc())
            if query:
                q = q.filter(ProofRow.query == query)
            rows = q.offset(offset).limit(limit).all()
            return [self._proof_row_to_dict(row) for row in rows]
        finally:
            session.close()

    def get_proof(self, proof_id: str) -> Optional[dict]:
        """Fetch a single proof by ID."""
        session = self._Session()
        try:
            row = session.get(ProofRow, proof_id)
            return self._proof_row_to_dict(row) if row else None
        finally:
            session.close()

    def list_inference_runs(
        self,
        query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Query persisted inference runs."""
        session = self._Session()
        try:
            q = session.query(InferenceRunRow).order_by(
                InferenceRunRow.created_at.desc()
            )
            if query:
                q = q.filter(InferenceRunRow.query == query)
            rows = q.offset(offset).limit(limit).all()
            return [self._inference_run_row_to_dict(row) for row in rows]
        finally:
            session.close()

    def get_inference_run(self, run_id: str) -> Optional[dict]:
        """Fetch a single inference run by ID."""
        session = self._Session()
        try:
            row = session.get(InferenceRunRow, run_id)
            return self._inference_run_row_to_dict(row) if row else None
        finally:
            session.close()

    def record_contradiction(self, report: ContradictionReport) -> str:
        """Persist a detected contradiction."""
        contradiction_id = str(uuid.uuid4())
        session = self._Session()
        try:
            row = ContradictionRow(
                id=contradiction_id,
                namespace=self.namespace,
                fact1_predicate=str(report.fact1.predicate),
                fact2_predicate=str(report.fact2.predicate),
                explanation=report.explanation,
                kb_snapshot=self.snapshot(),
            )
            session.add(row)
            session.commit()
        finally:
            session.close()
        return contradiction_id

    def list_contradictions(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Query persisted contradiction records for this namespace."""
        session = self._Session()
        try:
            rows = (
                session.query(ContradictionRow)
                .filter_by(namespace=self.namespace)
                .order_by(ContradictionRow.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return [self._contradiction_row_to_dict(row) for row in rows]
        finally:
            session.close()

    def detect_contradictions(self) -> list[ContradictionReport]:
        """Detect contradictions and persist new reports."""
        reports = super().detect_contradictions()
        existing = {
            (row["fact1"], row["fact2"])
            for row in self.list_contradictions(limit=1000)
        }
        for report in reports:
            key = (str(report.fact1.predicate), str(report.fact2.predicate))
            rev = (key[1], key[0])
            if key not in existing and rev not in existing:
                self.record_contradiction(report)
                existing.add(key)
        return reports

    @staticmethod
    def _proof_row_to_dict(row: ProofRow) -> dict:
        return {
            "id": row.id,
            "query": row.query,
            "result": row.result,
            "proof_json": row.proof_json,
            "run_hash": row.run_hash,
            "created_at": row.created_at.isoformat(),
        }

    @staticmethod
    def _inference_run_row_to_dict(row: InferenceRunRow) -> dict:
        return {
            "id": row.id,
            "query": row.query,
            "mode": row.mode,
            "result": row.result,
            "duration_ms": row.duration_ms,
            "kb_snapshot": row.kb_snapshot,
            "run_hash": row.run_hash,
            "created_at": row.created_at.isoformat(),
        }

    @staticmethod
    def _contradiction_row_to_dict(row: ContradictionRow) -> dict:
        return {
            "id": row.id,
            "namespace": row.namespace,
            "fact1": row.fact1_predicate,
            "fact2": row.fact2_predicate,
            "explanation": row.explanation,
            "kb_snapshot": row.kb_snapshot,
            "created_at": row.created_at.isoformat(),
        }

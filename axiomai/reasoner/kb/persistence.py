"""
SQLite-backed persistent knowledge base.
"""

from __future__ import annotations

import json
import uuid
from typing import Optional

from ..core.models import Fact, Predicate, Rule
from .schema import FactRow, InferenceRunRow, ProofRow, RuleRow, create_session_factory
from .store import KnowledgeBase


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

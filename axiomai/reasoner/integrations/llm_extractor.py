"""
LLM Extractor — Extract facts and rules from natural language.
Uses structured JSON output to constrain LLM responses.
"""

from __future__ import annotations

import re
from typing import Any

from ..core.models import Fact, Predicate, Rule
from ..core.parser import Parser, ParserError
from .llm_client import LLMClient, create_llm_client


class LLMExtractor:
    """
    Extract structured facts and rules from natural language using LLM.

    IMPORTANT: LLM only translates. The reasoning engine does the proving.

    Usage:
        extractor = LLMExtractor()  # uses env or fallback
        result = extractor.extract("Socrates is a human. All humans are mortal.")
    """

    def __init__(self, llm_client: LLMClient | Any | None = None, model: str = "gpt-4o"):
        if llm_client is not None and not isinstance(llm_client, LLMClient):
            # Legacy OpenAI client duck-type support
            self._client: LLMClient | None = _LegacyOpenAIAdapter(llm_client, model)
        else:
            self._client = llm_client or create_llm_client()
        self._model = model
        self._parser = Parser()
        self._stats = {"extractions": 0, "failures": 0, "validated": 0, "rejected": 0}

    def extract(self, text: str) -> dict[str, list]:
        """Extract and validate facts and rules from natural language."""
        facts = self.extract_facts(text)
        rules = self.extract_rules(text)
        return {"facts": facts, "rules": rules}

    def extract_facts(self, text: str) -> list[Fact]:
        """Extract facts from natural language text."""
        self._stats["extractions"] += 1

        if not self._client:
            return self._fallback_extract_facts(text)

        try:
            data = self._client.complete_json(self._SYSTEM_PROMPT_FACTS, text, model=self._model)
            facts: list[Fact] = []
            for item in data.get("facts", []):
                try:
                    pred_str = item["predicate"]
                    source = item.get("source", "llm")
                    fact = Fact.create(pred_str, source=source, confidence_source="llm_extracted")
                    if self.validate_extraction(fact):
                        facts.append(fact)
                        self._stats["validated"] += 1
                    else:
                        self._stats["rejected"] += 1
                except Exception:
                    self._stats["rejected"] += 1
                    continue
            return facts
        except Exception:
            self._stats["failures"] += 1
            return self._fallback_extract_facts(text)

    def extract_rules(self, text: str) -> list[Rule]:
        """Extract IF-THEN rules from natural language."""
        self._stats["extractions"] += 1

        if not self._client:
            return self._fallback_extract_rules(text)

        try:
            data = self._client.complete_json(self._SYSTEM_PROMPT_RULES, text, model=self._model)
            rules: list[Rule] = []
            for item in data.get("rules", []):
                try:
                    rule_str = item["rule"]
                    priority = item.get("priority", 1)
                    rule_obj = Rule.parse(rule_str, priority=priority)
                    rule_obj.confidence_source = "llm_extracted"
                    rule_obj.source = "llm"
                    if self.validate_extraction(rule_obj):
                        rules.append(rule_obj)
                        self._stats["validated"] += 1
                    else:
                        self._stats["rejected"] += 1
                except Exception:
                    self._stats["rejected"] += 1
                    continue
            return rules
        except Exception:
            self._stats["failures"] += 1
            return self._fallback_extract_rules(text)

    def _fallback_extract_facts(self, text: str) -> list[Fact]:
        """Rule-based fact extraction when no LLM client is available."""
        facts = []
        patterns = [
            r"(\w+)\s+is\s+(?:a\s+)?(\w+)",
            r"(\w+)\s+are\s+(\w+)",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                entity, type_ = match.groups()
                try:
                    pred = Predicate.parse(f"{type_.capitalize()}({entity.capitalize()})")
                    fact = Fact.create(pred, source="fallback", confidence_source="derived")
                    if self.validate_extraction(fact):
                        facts.append(fact)
                except ParserError:
                    continue
        return facts

    def _fallback_extract_rules(self, text: str) -> list[Rule]:
        """Rule-based rule extraction when no LLM client is available."""
        rules = []
        all_match = re.findall(r"all\s+(\w+)\s+are\s+(\w+)", text, re.IGNORECASE)
        for subject, predicate in all_match:
            try:
                subject_singular = subject.rstrip("s").capitalize()
                pred_cap = predicate.capitalize()
                rule_obj = Rule.parse(f"IF {subject_singular}(x) THEN {pred_cap}(x)")
                if self.validate_extraction(rule_obj):
                    rules.append(rule_obj)
            except ParserError:
                continue
        return rules

    def validate_extraction(self, item: Fact | Rule) -> bool:
        """Validate that an extracted fact/rule is well-formed."""
        if isinstance(item, Fact):
            pred = item.predicate
            return bool(pred.relation) and len(pred.relation) >= 2
        if isinstance(item, Rule):
            return bool(item.consequent) and bool(item.antecedents)
        return False

    def stats(self) -> dict:
        return dict(self._stats)

    _SYSTEM_PROMPT_FACTS = """You are a fact extraction system. Given natural language text, extract all factual claims as predicates.

Output ONLY valid JSON with this structure:
{
  "facts": [
    {"predicate": "Relation(term1, term2)", "source": "extracted from text", "confidence": "high/medium/low"}
  ]
}

Rules:
- Use TitleCase for constants: Human(Socrates), NOT Human(socrates)
- Use lowercase for variables: Human(x), Loves(x, y)
- Extract ONLY explicitly stated facts
- Do NOT infer or derive new facts
- If no facts found, return {"facts": []}"""

    _SYSTEM_PROMPT_RULES = """You are a rule extraction system. Given natural language text, extract all IF-THEN rules.

Output ONLY valid JSON with this structure:
{
  "rules": [
    {"rule": "IF Human(x) THEN Mortal(x)", "priority": 1, "confidence": "high/medium/low"}
  ]
}

Rules:
- Use TitleCase for constants: Human(Socrates)
- Use lowercase for variables: Human(x), Parent(x, y)
- Only extract rules explicitly stated or strongly implied
- If no rules found, return {"rules": []}"""


class _LegacyOpenAIAdapter:
    """Wrap legacy OpenAI client objects behind LLMClient protocol."""

    def __init__(self, client: Any, model: str):
        self._client = client
        self._model = model

    def complete_json(self, system: str, user: str, *, model: str | None = None) -> dict:
        import json

        response = self._client.chat.completions.create(
            model=model or self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

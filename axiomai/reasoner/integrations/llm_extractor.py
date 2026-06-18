"""
LLM Extractor — Extract facts and rules from natural language.
Uses structured output (Pydantic) to constrain LLM responses.
"""

from __future__ import annotations

import json
from typing import Optional
from ..core.models import Fact, Rule, Predicate
from ..core.parser import Parser, ParserError


class LLMExtractor:
    """
    Extract structured facts and rules from natural language using LLM.

    IMPORTANT: LLM only translates. The reasoning engine does the proving.

    Usage:
        extractor = LLMExtractor(openai_client)
        facts, rules = extractor.extract("Socrates is a human. All humans are mortal.")
    """

    def __init__(self, llm_client=None):
        self._client = llm_client
        self._parser = Parser()
        self._stats = {"extractions": 0, "failures": 0}

    def extract_facts(self, text: str) -> list[Fact]:
        """Extract facts from natural language text."""
        self._stats["extractions"] += 1

        if not self._client:
            return self._fallback_extract_facts(text)

        try:
            response = self._client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self._SYSTEM_PROMPT_FACTS},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
            )
            data = json.loads(response.choices[0].message.content)
            facts = []
            for item in data.get("facts", []):
                try:
                    pred_str = item["predicate"]
                    source = item.get("source", "llm")
                    fact = Fact.create(pred_str, source=source, confidence_source="llm_extracted")
                    facts.append(fact)
                except Exception:
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
            response = self._client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self._SYSTEM_PROMPT_RULES},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
            )
            data = json.loads(response.choices[0].message.content)
            rules = []
            for item in data.get("rules", []):
                try:
                    rule_str = item["rule"]
                    priority = item.get("priority", 1)
                    rule_obj = Rule.parse(rule_str, priority=priority)
                    rule_obj.confidence_source = "llm_extracted"
                    rule_obj.source = "llm"
                    rules.append(rule_obj)
                except Exception:
                    continue
            return rules
        except Exception:
            self._stats["failures"] += 1
            return self._fallback_extract_rules(text)

    def _fallback_extract_facts(self, text: str) -> list[Fact]:
        """Rule-based fact extraction when no LLM client is available."""
        facts = []
        import re
        patterns = [
            r"(\w+)\s+is\s+(?:a\s+)?(\w+)",
            r"(\w+)\s+are\s+(\w+)",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                entity, type_ = match.groups()
                try:
                    pred = Predicate.parse(f"{type_.capitalize()}({entity.capitalize()})")
                    facts.append(Fact.create(pred, source="fallback", confidence_source="derived"))
                except ParserError:
                    continue
        return facts

    def _fallback_extract_rules(self, text: str) -> list[Rule]:
        """Rule-based rule extraction when no LLM client is available."""
        rules = []
        import re
        all_match = re.findall(r"all\s+(\w+)\s+are\s+(\w+)", text, re.IGNORECASE)
        for subject, predicate in all_match:
            try:
                subject_singular = subject.rstrip("s").capitalize()
                pred_cap = predicate.capitalize()
                rule_obj = Rule.parse(
                    f"IF {subject_singular}(x) THEN {pred_cap}(x)"
                )
                rules.append(rule_obj)
            except ParserError:
                continue
        return rules

    def validate_extraction(self, item) -> bool:
        """Validate that an extracted fact/rule is well-formed."""
        if isinstance(item, Fact):
            pred = item.predicate
            if not pred.relation:
                return False
            if len(pred.relation) < 2:
                return False
            return True
        if isinstance(item, Rule):
            if not item.consequent:
                return False
            if not item.antecedents:
                return False
            return True
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

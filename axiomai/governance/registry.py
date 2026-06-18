"""Policy registry — load governance policy packs by ID."""

from __future__ import annotations

from pathlib import Path

from axiomai.governance.policy import PolicyPack

_POLICIES_DIR = Path(__file__).resolve().parent / "policies"

_BUILTIN_POLICIES = {
    "refund-policy": "refund-policy.yaml",
    "procurement-policy": "procurement-policy.yaml",
    "data-access-policy": "data-access-policy.yaml",
    "cloud-cost-policy": "cloud-cost-policy.yaml",
}


class PolicyRegistry:
    """Resolve policy packs by identifier."""

    def __init__(self, policies_dir: Path | None = None):
        self._dir = policies_dir or _POLICIES_DIR
        self._cache: dict[str, PolicyPack] = {}

    def get(self, policy_id: str) -> PolicyPack:
        if policy_id in self._cache:
            return self._cache[policy_id]
        filename = _BUILTIN_POLICIES.get(policy_id)
        if not filename:
            raise KeyError(f"Unknown policy: {policy_id}")
        pack = PolicyPack.load(self._dir / filename)
        self._cache[policy_id] = pack
        return pack

    def list_policies(self) -> list[dict[str, str]]:
        return [
            {
                "id": policy_id,
                "name": self.get(policy_id).name,
                "version": self.get(policy_id).version,
                "action_type": self.get(policy_id).action_type,
            }
            for policy_id in sorted(_BUILTIN_POLICIES)
        ]

    @classmethod
    def default(cls) -> PolicyRegistry:
        return cls()

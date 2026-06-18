"""Mock connectors with synthetic enterprise evidence for offline demos."""

from __future__ import annotations

from axiomai.connectors.base import BaseConnector
from axiomai.reasoner.core.models import Fact


class AzureADConnector(BaseConnector):
    """Synthetic Azure AD identity facts."""

    source = "azure_ad"

    def fetch_evidence(self) -> list[Fact]:
        return self._facts_from_predicates([
            "User(alice@corp.example)",
            "User(bob@corp.example)",
            "MfaEnabled(alice@corp.example)",
            "MfaDisabled(bob@corp.example)",
            "PrivilegedRole(bob@corp.example, GlobalAdmin)",
        ])


class AWSConfigConnector(BaseConnector):
    """Synthetic AWS Config compliance facts."""

    source = "aws_config"

    def fetch_evidence(self) -> list[Fact]:
        return self._facts_from_predicates([
            "S3Bucket(public-logs)",
            "PublicAccessBlockDisabled(public-logs)",
            "EC2Instance(web-prod-1)",
            "SecurityGroupOpen(web-prod-1, 22)",
            "EncryptionEnabled(db-prod-1)",
        ])


class SIEMConnector(BaseConnector):
    """Synthetic SIEM security event facts."""

    source = "siem"

    def fetch_evidence(self) -> list[Fact]:
        return self._facts_from_predicates([
            "Event(login_failed)",
            "Source(ip_10_0_0_5)",
            "Target(user_admin)",
            "Event(lateral_movement)",
            "Source(host_workstation_12)",
        ])

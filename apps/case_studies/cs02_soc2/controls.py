"""SOC2 control definitions and compliance rules."""

from __future__ import annotations

from dataclasses import dataclass

SOC2_RULES = [
    # CC6.1 — MFA for privileged accounts
    "IF PrivilegedRole(u, r) AND MfaDisabled(u) THEN ControlGap_MFA(u)",
    "IF PrivilegedRole(u, r) AND MfaEnabled(u) THEN ControlPass_MFA(u)",
    # CC7.2 — Automated backup for production servers
    "IF ProductionServer(s) AND NotAutomatedBackup(s) THEN ControlGap_Backup(s)",
    "IF ProductionServer(s) AND AutomatedBackup(s) THEN ControlPass_Backup(s)",
    # CC7.3 — Log retention >= 90 days
    "IF System(s) AND RetentionBelow90(s) THEN ControlGap_LogRetention(s)",
    "IF System(s) AND RetentionAtLeast90(s) THEN ControlPass_LogRetention(s)",
    # CC6.2 — Access review within 30 days
    "IF UserAccount(u) AND AccessReviewOverdue(u) THEN ControlGap_AccessReview(u)",
    "IF UserAccount(u) AND AccessReviewCurrent(u) THEN ControlPass_AccessReview(u)",
    # CC8.1 — Change management approval
    "IF ChangeTicket(t) AND NotApproved(t) THEN ControlGap_ChangeMgmt(t)",
    "IF ChangeTicket(t) AND Approved(t) THEN ControlPass_ChangeMgmt(t)",
    # CC6.7 — Certificate management
    "IF SecretStore(s) AND CertificateExpired(s) THEN ControlGap_Certificate(s)",
    "IF SecretStore(s) AND CertificateValid(s) THEN ControlPass_Certificate(s)",
    # CC7.1 — EDR coverage
    "IF Endpoint(e) AND EdrAgentMissing(e) THEN ControlGap_EDR(e)",
    "IF Endpoint(e) AND EdrAgentInstalled(e) THEN ControlPass_EDR(e)",
    # CC6.6 — Network device hardening
    "IF NetworkDevice(n) AND DefaultCredentials(n) THEN ControlGap_Network(n)",
    "IF NetworkDevice(n) AND HardenedCredentials(n) THEN ControlPass_Network(n)",
]

SUPPLEMENTAL_FACTS = [
    "ProductionServer(web-prod-1)",
    "AutomatedBackup(web-prod-1)",
    "ProductionServer(legacy-db)",
    "NotAutomatedBackup(legacy-db)",
    "System(web-prod-1)",
    "RetentionAtLeast90(web-prod-1)",
    "System(legacy-app)",
    "RetentionBelow90(legacy-app)",
    "UserAccount(svc-backup)",
    "AccessReviewOverdue(svc-backup)",
    "UserAccount(alice@corp.example)",
    "AccessReviewCurrent(alice@corp.example)",
    "ChangeTicket(CHG-1042)",
    "NotApproved(CHG-1042)",
    "ChangeTicket(CHG-1043)",
    "Approved(CHG-1043)",
    "SecretStore(vault-prod)",
    "CertificateValid(vault-prod)",
    "SecretStore(legacy-vault)",
    "CertificateExpired(legacy-vault)",
    "Endpoint(workstation-12)",
    "EdrAgentInstalled(workstation-12)",
    "Endpoint(legacy-printer)",
    "EdrAgentMissing(legacy-printer)",
    "NetworkDevice(core-switch-1)",
    "HardenedCredentials(core-switch-1)",
    "NetworkDevice(guest-ap)",
    "DefaultCredentials(guest-ap)",
]


@dataclass
class ControlDefinition:
    control_id: str
    name: str
    gap_prefix: str
    pass_prefix: str
    severity: str = "High"


SOC2_CONTROLS = [
    ControlDefinition("CC6.1", "All privileged accounts require MFA", "ControlGap_MFA", "ControlPass_MFA"),
    ControlDefinition("CC7.2", "Production servers require automated backup", "ControlGap_Backup", "ControlPass_Backup"),
    ControlDefinition("CC7.3", "Log retention must be >= 90 days", "ControlGap_LogRetention", "ControlPass_LogRetention"),
    ControlDefinition("CC6.2", "Access changes reviewed within 30 days", "ControlGap_AccessReview", "ControlPass_AccessReview"),
    ControlDefinition("CC8.1", "Changes require approval", "ControlGap_ChangeMgmt", "ControlPass_ChangeMgmt"),
    ControlDefinition("CC6.7", "Certificates must be valid", "ControlGap_Certificate", "ControlPass_Certificate"),
    ControlDefinition("CC7.1", "Endpoints require EDR agent", "ControlGap_EDR", "ControlPass_EDR"),
    ControlDefinition("CC6.6", "Network devices must not use default credentials", "ControlGap_Network", "ControlPass_Network"),
]

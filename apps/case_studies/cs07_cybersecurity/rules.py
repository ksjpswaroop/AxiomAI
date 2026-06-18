"""MITRE-aligned attack chain rules for ransomware detection."""

ATTACK_CHAIN_RULES = [
    # Initial access
    "IF EmailClick(x) AND PowerShellLaunched(x) AND EncodedCommand(x) THEN ProbableInitialAccess(x)",
    "IF EmailClick(x) AND OpenedAttachment(x) THEN PhishingVector(x)",
    # Execution
    "IF PowerShellLaunched(x) AND EncodedCommand(x) THEN PowerShellExecution(x)",
    "IF PowerShellLaunched(x) AND ScheduledTaskCreated(x) THEN ProbablePersistence(x)",
    # C2
    "IF EncodedCommand(x) AND C2Traffic(h) THEN ProbableC2Stage(h)",
    "IF C2Traffic(h) AND BeaconPattern(h) THEN ProbableC2Communication(h)",
    "IF OutboundTrafficSpike(h) AND C2Traffic(h) THEN ProbableC2Communication(h)",
    # Lateral movement
    "IF AdminCredentialUse(a, h) AND UnusualHostAccess(a, h) THEN ProbableLateralMovement(h)",
    "IF LateralMovementDetected(h) THEN ProbableLateralMovement(h)",
    # Impact / confirmation (host-centric with independent user variable)
    "IF FileEncryptionStarted(h) THEN ImpactEncryption(h)",
    "IF ImpactEncryption(h) AND ProbableC2Communication(h) AND ProbableInitialAccess(x) THEN ConfirmedRansomware(h)",
    "IF ImpactEncryption(h) AND ProbableC2Communication(h) AND ProbableLateralMovement(h) AND PhishingVector(x) THEN ConfirmedRansomwareChain(h)",
]

CAUSAL_EDGES = [
    ("PhishingVector", "PowerShellExecution"),
    ("PowerShellExecution", "ProbableC2Communication"),
    ("ProbableC2Communication", "ProbableLateralMovement"),
    ("ProbableLateralMovement", "ImpactEncryption"),
]

CHAIN_LABELS = {
    "PhishingVector": "[INITIAL ACCESS] Phishing email clicked",
    "ProbableInitialAccess": "[INITIAL ACCESS] Phishing email clicked",
    "PowerShellExecution": "[EXECUTION] PowerShell launched",
    "ProbableC2Communication": "[C2] Command and control",
    "ProbableC2Stage": "[C2] Command and control",
    "ProbableLateralMovement": "[LATERAL] Admin credentials used",
    "ImpactEncryption": "[IMPACT] File encryption started",
}

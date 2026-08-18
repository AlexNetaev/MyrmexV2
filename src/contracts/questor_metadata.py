from pydantic import BaseModel, ConfigDict, Field

from src.contracts.enums import RedactionLevel, RetentionClass


class LocalAuditRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    blackbox_id: str = Field(..., min_length=1)
    manifest_checksum: str = Field(..., min_length=1)
    blackbox_digest: str = Field(..., min_length=1)
    redaction_level: RedactionLevel = RedactionLevel.STRONG
    retention_class: RetentionClass = RetentionClass.NORMAL
    access_policy_summary: str = Field(..., min_length=1)


class OperationalMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    oom_count: int = Field(default=0, ge=0)
    timeout_count: int = Field(default=0, ge=0)
    lease_wait_time_s: float = Field(default=0.0, ge=0.0)
    lease_denied_count: int = Field(default=0, ge=0)
    lease_queued_timeout_count: int = Field(default=0, ge=0)
    capability_retry_count: int = Field(default=0, ge=0)
    hal_command_duplicate_blocked_count: int = Field(default=0, ge=0)
    llm_advice_rejected_count: int = Field(default=0, ge=0)
    llm_advice_timeout_count: int = Field(default=0, ge=0)
    branch_condition_unresolved_count: int = Field(default=0, ge=0)
    recovery_attempts: int = Field(default=0, ge=0)
    recovery_lock_denied_count: int = Field(default=0, ge=0)


class QuestorMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    questor_version: str | None = None
    policy_version: str | None = None
    local_audit: LocalAuditRef | None = None
    operational_metrics: OperationalMetrics | None = None
    # Felder für Questor-Instanz und Sequenz (von Tests erwartet)
    questor_instance_id: str | None = None
    sequence_number: int | None = None

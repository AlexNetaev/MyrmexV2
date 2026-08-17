from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.contracts.enums import AbbruchKlasse, ErgebnisStatus
from src.contracts.questor_metadata import QuestorMetadata
from src.contracts.research_package import ID_PATTERN


class QuestorErgebnisPaket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_id: str = Field(
        ...,
        pattern=ID_PATTERN,
        min_length=1,
        max_length=128,
    )
    zyklus_id: str = Field(
        ...,
        pattern=ID_PATTERN,
        min_length=1,
        max_length=128,
    )
    attempt_id: int = Field(..., ge=0, le=999_999, strict=True)
    idempotency_key: str | None = None

    questor_instance_id: str = Field(..., min_length=1)
    sequence_number: int = Field(..., ge=0)
    observed_atlas_version_id: str = Field(..., min_length=1)

    status: ErgebnisStatus
    abbruch_grund: str | None = None
    abbruch_klasse: AbbruchKlasse

    routing_checkpoint: dict[str, Any] = Field(default_factory=dict)
    ergebnis_daten: dict[str, Any] = Field(default_factory=dict)
    validierung: dict[str, Any] = Field(default_factory=dict)

    kristall_kandidaten: list[dict[str, Any]] = Field(default_factory=list)
    gefahren_beobachtet: list[str] = Field(default_factory=list)
    signale_fuer_atlas: list[dict[str, Any]] = Field(default_factory=list)

    vollstaendig_flag: bool
    rohdaten_checksumme: str = Field(..., min_length=1)

    questor_metadata: QuestorMetadata | None = None

    @model_validator(mode="after")
    def _validate_result(self) -> "QuestorErgebnisPaket":
        expected = f"{self.package_id}:{self.zyklus_id}:{self.attempt_id}"

        if len(expected) > 264:
            raise ValueError("PACKAGE_INVALID")

        if not self.idempotency_key:
            self.idempotency_key = expected
        elif self.idempotency_key != expected:
            raise ValueError("PACKAGE_INVALID")

        if self.status == ErgebnisStatus.ERFOLGREICH:
            if self.abbruch_grund is not None:
                raise ValueError("PACKAGE_INVALID")
            if self.abbruch_klasse != AbbruchKlasse.OPERATIONAL:
                raise ValueError("PACKAGE_INVALID")
        else:
            if self.abbruch_grund is None:
                raise ValueError("PACKAGE_INVALID")

        return self

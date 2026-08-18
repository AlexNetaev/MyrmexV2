"""Seher — LLM-basierte Sicherheitsprüfung (Stub für Phase 6a)."""

from src.contracts.enums import SeherResult


class Seher:
    """
    Der Seher — LLM-basierte Sicherheitsprüfung.

    In Phase 6a ist dies ein Stub, der immer SEHER_PASS zurückgibt.
    Die vollständige Implementierung erfolgt in Phase 6b.

    Wichtige Regeln:
    - Seher schreibt niemals direkt rote Signale
    - Veto nur mit Evidenz (Phase 6b)
    - Berufung über Kanzler (Phase 6b)
    """

    def __init__(self):
        pass

    def seher_check(self, package, kontext=None) -> SeherResult:
        """
        Führt die Seher-Prüfung durch.

        Args:
            package: ResearchPackage zur Prüfung
            kontext: Zusätzlicher Kontext für die Prüfung

        Returns:
            SeherResult: Aktuell immer SEHER_PASS (Stub)
        """
        # Stub-Implementierung für Phase 6a
        # Vollständige Implementierung in Phase 6b mit LLM
        return SeherResult.SEHER_PASS

    def is_llm_based(self) -> bool:
        """Bestätigt, dass der Seher LLM-basiert arbeitet."""
        # In Phase 6a: False (Stub)
        # In Phase 6b: True (vollständige LLM-Implementierung)
        return False

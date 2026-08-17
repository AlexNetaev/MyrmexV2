from enum import Enum


class ErgebnisStatus(str, Enum):
    ERFOLGREICH = "erfolgreich"
    FEHLGESCHLAGEN = "fehlgeschlagen"
    ABGEBROCHEN = "abgebrochen"


class AbbruchKlasse(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    SCIENTIFIC = "SCIENTIFIC"
    SAFETY = "SAFETY"


class SecurityMode(str, Enum):
    NORMAL = "NORMAL"
    SANDBOX = "SANDBOX"
    DEV_SANDBOX_ONLY = "DEV_SANDBOX_ONLY"
    RECOVERY = "RECOVERY"


class DispatchMode(str, Enum):
    NORMAL = "NORMAL"
    RETRY = "RETRY"
    RECOVERY = "RECOVERY"


class GateMode(str, Enum):
    NORMAL = "NORMAL"
    FRACTURE_DIAGNOSIS = "FRACTURE_DIAGNOSIS"
    HIGH_RISK_OVERRIDE = "HIGH_RISK_OVERRIDE"
    SANDBOX = "SANDBOX"


class ResourceClass(str, Enum):
    LAB_ACTUATOR = "LAB_ACTUATOR"
    COMPUTE_NODE = "COMPUTE_NODE"
    SIMULATION_ENVIRONMENT = "SIMULATION_ENVIRONMENT"
    SANDBOX_ENVIRONMENT = "SANDBOX_ENVIRONMENT"
    HYBRID_SLOT = "HYBRID_SLOT"


class LockPolicy(str, Enum):
    EXCLUSIVE = "EXCLUSIVE"
    SINGLE_OCCUPANT = "SINGLE_OCCUPANT"
    PATH_RESERVATION = "PATH_RESERVATION"
    CONTAINER_LOCK = "CONTAINER_LOCK"


class SlotStatus(str, Enum):
    FREE = "FREE"
    RESERVED = "RESERVED"
    ACTIVE = "ACTIVE"
    ERROR = "ERROR"
    ESTOP_SUSPENDED = "ESTOP_SUSPENDED"
    INTERLOCKED = "INTERLOCKED"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"


class ZoneStatus(str, Enum):
    FREE = "FREE"
    LOCKED = "LOCKED"
    PATH_RESERVED = "PATH_RESERVED"
    ESTOP_SUSPENDED = "ESTOP_SUSPENDED"
    INTERLOCKED = "INTERLOCKED"
    MAINTENANCE = "MAINTENANCE"


class ProcessLifecycleState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    SAFE_HOLD = "SAFE_HOLD"
    WAITING_FOR_RELEASE = "WAITING_FOR_RELEASE"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"
    FAULT = "FAULT"
    UNKNOWN = "UNKNOWN"


class ProcessMode(str, Enum):
    START = "START"
    MONITOR = "MONITOR"
    RESUME = "RESUME"
    HOLD = "HOLD"
    ABORT = "ABORT"
    RELEASE_STAGE = "RELEASE_STAGE"


class OnLeaseExpiryPolicy(str, Enum):
    SAFE_HOLD = "SAFE_HOLD"
    ABORT_TO_SAFE_STATE = "ABORT_TO_SAFE_STATE"
    CONTINUE_PASSIVE_SAFE = "CONTINUE_PASSIVE_SAFE"
    REQUIRES_RECONCILE = "REQUIRES_RECONCILE"


class ReleaseAuthority(str, Enum):
    QUESTOR = "QUESTOR"
    SAFETY_PROCESS = "SAFETY_PROCESS"
    HUMAN = "HUMAN"
    KANZLER = "KANZLER"
    SAFETY_PROCESS_OR_HUMAN = "SAFETY_PROCESS_OR_HUMAN"


class RequestSource(str, Enum):
    QUESTOR = "QUESTOR"
    MAINTENANCE = "MAINTENANCE"
    TEST = "TEST"


class HALCommandResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    DENIED = "DENIED"
    TIMEOUT = "TIMEOUT"
    ESTOP = "ESTOP"
    INTERLOCK = "INTERLOCK"
    ERROR = "ERROR"
    DUPLICATE_BLOCKED = "DUPLICATE_BLOCKED"
    LEASE_INVALID = "LEASE_INVALID"
    LEASE_EXPIRED = "LEASE_EXPIRED"
    SLOT_UNAVAILABLE = "SLOT_UNAVAILABLE"
    ZONE_LOCK_UNAVAILABLE = "ZONE_LOCK_UNAVAILABLE"


class ErrorClass(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    SAFETY = "SAFETY"


class CommandLifecycleState(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATING = "VALIDATING"
    ACCEPTED = "ACCEPTED"
    EXECUTING = "EXECUTING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    DENIED = "DENIED"
    ESTOP = "ESTOP"
    INTERLOCK = "INTERLOCK"
    DUPLICATE_BLOCKED = "DUPLICATE_BLOCKED"


class EstopStateName(str, Enum):
    NORMAL = "NORMAL"
    ACTIVE = "ACTIVE"
    LATCHED = "LATCHED"
    TEST = "TEST"


class EstopOrigin(str, Enum):
    SOFTWARE = "SOFTWARE"
    HARDWARE_INTERLOCK = "HARDWARE_INTERLOCK"
    EXTERNAL_SAFETY_CHAIN = "EXTERNAL_SAFETY_CHAIN"


class RedactionLevel(str, Enum):
    NONE = "NONE"
    BASIC = "BASIC"
    STRONG = "STRONG"


class RetentionClass(str, Enum):
    NORMAL = "NORMAL"
    SAFETY_HOLD = "SAFETY_HOLD"
    DEVELOPMENT_HOLD = "DEVELOPMENT_HOLD"


class SignalType(str, Enum):
    """SignalType: Typ eines Atlas-Signals."""

    SCIENTIFIC = "SCIENTIFIC"
    SAFETY = "SAFETY"
    OPERATIONAL = "OPERATIONAL"
    SYSTEM = "SYSTEM"


class SignalSeverity(str, Enum):
    """SignalSeverity: Priorität eines Signals für Resolution."""

    RED = "RED"  # Highest priority
    YELLOW = "YELLOW"
    PURPLE = "PURPLE"
    GREEN = "GREEN"
    WHITE = "WHITE"  # Lowest priority


class PackageStatus(str, Enum):
    """PackageStatus: Status eines ResearchPackage im Archivar."""

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED_DUPLICATE = "REJECTED_DUPLICATE"
    REJECTED_SEQUENCE = "REJECTED_SEQUENCE"
    DRAFT_RECOVERABLE = "DRAFT_RECOVERABLE"
    CRYSTALLIZED = "CRYSTALLIZED"


class EventType(str, Enum):
    """EventType: Typ eines Events im Event-Sourcing-Log."""

    OPERATIONAL_EVENT = "OPERATIONAL_EVENT"
    SCIENTIFIC_SIGNAL = "SCIENTIFIC_SIGNAL"
    SAFETY_SIGNAL = "SAFETY_SIGNAL"
    CRYSTAL_CREATED = "CRYSTAL_CREATED"
    SNAPSHOT_CREATED = "SNAPSHOT_CREATED"


class MissingDataPolicy(str, Enum):
    """MissingDataPolicy: Behandlung von UNKNOWN-Dimensionen beim Clustering."""

    EXCLUDE_DIMENSION = "EXCLUDE_DIMENSION"
    IMPUTE_MEDIAN = "IMPUTE_MEDIAN"
    SEPARATE_CLUSTER = "SEPARATE_CLUSTER"


class DimensionStatus(str, Enum):
    """DimensionStatus: Status einer Dimension in einem Kristall."""

    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"


class ZoneHealth(str, Enum):
    """ZoneHealth: Gesundheitszustand einer Zone basierend auf fracture_score."""

    STABIL = "STABIL"
    INSTABIL = "INSTABIL"
    QUARANTAENE = "QUARANTAENE"
    GESPERRT = "GESPERRT"


class NormalizationPolicy(str, Enum):
    """NormalizationPolicy: Strategie zur Normalisierung von Koordinaten."""

    MIN_MAX = "MIN_MAX"
    Z_SCORE = "Z_SCORE"
    NONE = "NONE"

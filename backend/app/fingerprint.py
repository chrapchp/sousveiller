import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DeviceFeatures:
    service_uuids:  list[str]       = field(default_factory=list)
    mfr_data:       Optional[str]   = None
    tx_power:       Optional[int]   = None
    adv_interval_ms: Optional[int]  = None
    name:           Optional[str]   = None


class FingerprintStrategy(ABC):
    name: str  # stored alongside every fingerprint row for provenance

    @abstractmethod
    def compute(self, features: DeviceFeatures) -> Optional[str]:
        """Return a fingerprint hash, or None when signal is insufficient."""

    @abstractmethod
    def key_components(self, features: DeviceFeatures) -> dict[str, str]:
        """Return the input components stored for human inspection."""


class DeterministicHashStrategy(FingerprintStrategy):
    """
    SHA-256 of (sorted service UUIDs + manufacturer data prefix).
    Returns None when both signals are absent — too ambiguous to fingerprint.

    Stable across MAC rotations for the vast majority of consumer devices that
    broadcast fixed service UUIDs or a constant manufacturer data prefix.
    """
    name = "deterministic_hash_v1"

    def __init__(self, mfr_prefix_bytes: int = 3):
        self._prefix_len = mfr_prefix_bytes * 2  # hex chars

    def compute(self, features: DeviceFeatures) -> Optional[str]:
        uuids_key = self._uuids_key(features.service_uuids)
        mfr_key   = self._mfr_prefix(features.mfr_data)
        if not uuids_key and not mfr_key:
            return None
        canonical = f"uuids:{uuids_key}|mfr:{mfr_key}"
        return hashlib.sha256(canonical.encode()).hexdigest()

    def key_components(self, features: DeviceFeatures) -> dict[str, str]:
        return {
            "service_uuids_key": self._uuids_key(features.service_uuids),
            "mfr_prefix":        self._mfr_prefix(features.mfr_data),
        }

    def _uuids_key(self, uuids: list[str]) -> str:
        return ",".join(sorted(u.lower() for u in uuids))

    def _mfr_prefix(self, mfr_data: Optional[str]) -> str:
        if not mfr_data:
            return ""
        return mfr_data.lower()[: self._prefix_len]


# Strategy registry — add new strategies here (e.g. JaccardSimilarityStrategy,
# MLClusterStrategy) to make them available without touching call sites.
_strategies: dict[str, FingerprintStrategy] = {
    DeterministicHashStrategy.name: DeterministicHashStrategy(),
}
_active_name: str = DeterministicHashStrategy.name


def get_active_strategy() -> FingerprintStrategy:
    return _strategies[_active_name]


def get_strategy(name: str) -> Optional[FingerprintStrategy]:
    return _strategies.get(name)


def compute_fingerprint(features: DeviceFeatures) -> tuple[Optional[str], dict[str, str]]:
    """
    Returns (hash, key_components) using the active strategy.
    hash is None when the active strategy cannot fingerprint these features.
    """
    strategy   = get_active_strategy()
    fp_hash    = strategy.compute(features)
    components = strategy.key_components(features) if fp_hash else {}
    return fp_hash, components


def features_from_device_in(dev) -> DeviceFeatures:
    return DeviceFeatures(
        service_uuids=dev.service_uuids or [],
        mfr_data=dev.manufacturer_data,
        tx_power=dev.tx_power,
        adv_interval_ms=dev.adv_interval_ms,
        name=dev.name,
    )

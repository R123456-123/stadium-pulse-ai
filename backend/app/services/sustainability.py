"""Queue-linked sustainability estimation.

Computes energy consumption and waste generation estimates
based on zone occupancy. These are clearly labeled as
*estimates* in the UI and README — not real sensor data.

Model assumptions (documented for transparency):
    Energy: Base load per zone (lighting, HVAC baseline) plus
    a per-person increment (ventilation scaling, screens, etc.).
    Waste: Linear model based on average waste per person per
    hour at large sporting events (~0.12 kg/person/hour from
    published stadium sustainability reports).
"""

from __future__ import annotations

# ── Energy Estimation ────────────────────────────────────────

# Base energy draw (kW) for an empty zone by type
_BASE_ENERGY_KW: dict[str, float] = {
    "seating": 50.0,    # Field lighting, scoreboard, basic HVAC
    "concourse": 30.0,  # Corridor lighting, signage
    "vip": 25.0,        # Climate-controlled but smaller
}

# Additional energy per person (kW) — covers ventilation scaling,
# screen brightness adjustments, point-of-sale systems, etc.
_PER_PERSON_KW = 0.015  # 15W per person


def estimate_energy_kw(occupancy: int, zone_type: str) -> float:
    """Estimate energy consumption in kW for a zone.

    Args:
        occupancy: Current number of people in the zone.
        zone_type: One of "seating", "concourse", "vip".

    Returns:
        Estimated energy consumption in kilowatts.
    """
    base = _BASE_ENERGY_KW.get(zone_type, 20.0)
    return round(base + (occupancy * _PER_PERSON_KW), 2)


# ── Waste Estimation ────────────────────────────────────────

# Average waste per person per hour (kg) at a stadium event.
# Source: typical figures from stadium sustainability reports.
_WASTE_PER_PERSON_PER_HOUR = 0.12  # kg


def estimate_waste_kg(occupancy: int, interval_seconds: int) -> float:
    """Estimate waste generated in kg over a time interval.

    Args:
        occupancy: Current number of people in the zone.
        interval_seconds: Length of the time interval in seconds.

    Returns:
        Estimated waste generated in kilograms.
    """
    hours = interval_seconds / 3600
    return round(occupancy * _WASTE_PER_PERSON_PER_HOUR * hours, 3)

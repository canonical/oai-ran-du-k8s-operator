# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Define a dictionary where SCS values map to bandwidths and their guard bands."""

import logging

from frequency import Frequency

logger = logging.getLogger(__name__)


class GuardBandError(Exception):
    """Exception raised when guard band calculation fails."""

    pass


_minimum_guard_bands = {
    # SCS = 15 kHz
    Frequency.from_khz(15): {
        # Bandwidth             Guard Band
        Frequency.from_mhz(5): Frequency.from_khz("242.5"),
        Frequency.from_mhz(10): Frequency.from_khz("312.5"),
        Frequency.from_mhz(15): Frequency.from_khz("382.5"),
        Frequency.from_mhz(20): Frequency.from_khz("452.5"),
        Frequency.from_mhz(25): Frequency.from_khz("552.5"),
        Frequency.from_mhz(30): Frequency.from_khz("592.5"),
        Frequency.from_mhz(40): Frequency.from_khz("552.5"),
        Frequency.from_mhz(50): Frequency.from_khz("692.5"),
    },
    # SCS = 30 kHz
    Frequency.from_khz(30): {
        # Bandwidth             Guard Band
        Frequency.from_mhz(5): Frequency.from_khz(505),
        Frequency.from_mhz(10): Frequency.from_khz(665),
        Frequency.from_mhz(15): Frequency.from_khz(645),
        Frequency.from_mhz(20): Frequency.from_khz(805),
        Frequency.from_mhz(25): Frequency.from_khz(785),
        Frequency.from_mhz(30): Frequency.from_khz(945),
        Frequency.from_mhz(40): Frequency.from_khz(905),
        Frequency.from_mhz(50): Frequency.from_khz(1045),
        Frequency.from_mhz(60): Frequency.from_khz(825),
        Frequency.from_mhz(70): Frequency.from_khz(965),
        Frequency.from_mhz(80): Frequency.from_khz(925),
        Frequency.from_mhz(90): Frequency.from_khz(885),
        Frequency.from_mhz(100): Frequency.from_khz(845),
    },
    # SCS = 60 kHz
    Frequency.from_khz(60): {
        # Bandwidth             Guard Band
        Frequency.from_mhz(10): Frequency.from_khz(1010),
        Frequency.from_mhz(15): Frequency.from_khz(990),
        Frequency.from_mhz(20): Frequency.from_khz(1330),
        Frequency.from_mhz(25): Frequency.from_khz(1310),
        Frequency.from_mhz(30): Frequency.from_khz(1290),
        Frequency.from_mhz(40): Frequency.from_khz(1610),
        Frequency.from_mhz(50): Frequency.from_khz(1570),
        Frequency.from_mhz(60): Frequency.from_khz(1530),
        Frequency.from_mhz(70): Frequency.from_khz(1490),
        Frequency.from_mhz(80): Frequency.from_khz(1450),
        Frequency.from_mhz(90): Frequency.from_khz(1410),
        Frequency.from_mhz(100): Frequency.from_khz(1370),
    },
}


def get_minimum_guard_band(subcarrier_spacing: Frequency, bandwidth: Frequency) -> Frequency:
    """Retrieve the minimum guard band for a given subcarrier spacing and bandwidth.

    Args:
        subcarrier_spacing (Frequency): The subcarrier spacing in Frequency
        bandwidth (Frequency): The bandwidth in Frequency

    Returns:
        guard_band (Frequency): The minimum guard band in Frequency.

    Raises:
        GuardBandError: If the guard band is not found.
    """
    scs_data = _minimum_guard_bands.get(subcarrier_spacing)
    if scs_data:
        guard_band = scs_data.get(bandwidth)
        if guard_band:
            logger.info(
                "Calculated minimum guard band for SCS=%s and bandwidth=%s: %s",
                subcarrier_spacing,
                bandwidth,
                guard_band,
            )
            return guard_band

        logger.error(
            "Requested guard band for SCS=%s and bandwidth=%s not found.",
            subcarrier_spacing,
            bandwidth,
        )
        raise GuardBandError(
            f"No guard band found for bandwidth={bandwidth} and SCS={subcarrier_spacing}."
        )

    logger.error("Requested guard band for SCS=%s not found.", subcarrier_spacing)
    raise GuardBandError(f"No guard band found for SCS={subcarrier_spacing}.")

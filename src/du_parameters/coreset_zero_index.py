# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate the configuration index of CORESET 0.

Only FR1 is supported.
Only cases where SSB SCS and PDCCH SCS are equal.

Reference: 3GPP TS 38.213 version 17.1.0 Release 17, Chapter 13
https://www.etsi.org/deliver/etsi_ts/138200_138299/138213/17.01.00_60/ts_138213v170100p.pdf
"""

import logging
from dataclasses import dataclass
from typing import List

from .fr1_bands import ALLOWED_CHANNEL_BANDWIDTHS
from .frequency import Frequency

logger = logging.getLogger(__name__)


class CoresetZeroConfigurationIndexError(Exception):
    """Exception raised if CORESET 0 configuration index can't be determined."""

    pass


@dataclass
class CoresetZeroIndex:
    """CORESET 0 index configuration."""

    index: int
    coreset_rbs: int
    coreset_ofdm_symbols: int
    coreset_offset_rbs: int


# SCS = 15 kHz, bands with minimal channel bandwidth of 5 MHz or 10 MHz
TABLE_13_1 = [
    CoresetZeroIndex(index=0, coreset_rbs=24, coreset_ofdm_symbols=2, coreset_offset_rbs=0),
    CoresetZeroIndex(index=1, coreset_rbs=24, coreset_ofdm_symbols=2, coreset_offset_rbs=2),
    CoresetZeroIndex(index=2, coreset_rbs=24, coreset_ofdm_symbols=2, coreset_offset_rbs=4),
    CoresetZeroIndex(index=3, coreset_rbs=24, coreset_ofdm_symbols=3, coreset_offset_rbs=0),
    CoresetZeroIndex(index=4, coreset_rbs=24, coreset_ofdm_symbols=3, coreset_offset_rbs=2),
    CoresetZeroIndex(index=5, coreset_rbs=24, coreset_ofdm_symbols=3, coreset_offset_rbs=4),
    CoresetZeroIndex(index=6, coreset_rbs=48, coreset_ofdm_symbols=1, coreset_offset_rbs=12),
    CoresetZeroIndex(index=7, coreset_rbs=48, coreset_ofdm_symbols=1, coreset_offset_rbs=16),
    CoresetZeroIndex(index=8, coreset_rbs=48, coreset_ofdm_symbols=2, coreset_offset_rbs=12),
    CoresetZeroIndex(index=9, coreset_rbs=48, coreset_ofdm_symbols=2, coreset_offset_rbs=16),
    CoresetZeroIndex(index=10, coreset_rbs=48, coreset_ofdm_symbols=3, coreset_offset_rbs=12),
    CoresetZeroIndex(index=11, coreset_rbs=48, coreset_ofdm_symbols=3, coreset_offset_rbs=16),
    CoresetZeroIndex(index=12, coreset_rbs=96, coreset_ofdm_symbols=1, coreset_offset_rbs=38),
    CoresetZeroIndex(index=13, coreset_rbs=96, coreset_ofdm_symbols=2, coreset_offset_rbs=38),
    CoresetZeroIndex(index=14, coreset_rbs=96, coreset_ofdm_symbols=3, coreset_offset_rbs=38),
]

# SCS = 30 kHz, bands with minimal channel bandwidth of 5 MHz or 10 MHz
TABLE_13_4 = [
    CoresetZeroIndex(index=0, coreset_rbs=24, coreset_ofdm_symbols=2, coreset_offset_rbs=0),
    CoresetZeroIndex(index=1, coreset_rbs=24, coreset_ofdm_symbols=2, coreset_offset_rbs=1),
    CoresetZeroIndex(index=2, coreset_rbs=24, coreset_ofdm_symbols=2, coreset_offset_rbs=2),
    CoresetZeroIndex(index=3, coreset_rbs=24, coreset_ofdm_symbols=2, coreset_offset_rbs=3),
    CoresetZeroIndex(index=4, coreset_rbs=24, coreset_ofdm_symbols=2, coreset_offset_rbs=4),
    CoresetZeroIndex(index=5, coreset_rbs=24, coreset_ofdm_symbols=3, coreset_offset_rbs=0),
    CoresetZeroIndex(index=6, coreset_rbs=24, coreset_ofdm_symbols=3, coreset_offset_rbs=1),
    CoresetZeroIndex(index=7, coreset_rbs=24, coreset_ofdm_symbols=3, coreset_offset_rbs=2),
    CoresetZeroIndex(index=8, coreset_rbs=24, coreset_ofdm_symbols=3, coreset_offset_rbs=3),
    CoresetZeroIndex(index=9, coreset_rbs=24, coreset_ofdm_symbols=3, coreset_offset_rbs=4),
    CoresetZeroIndex(index=10, coreset_rbs=48, coreset_ofdm_symbols=1, coreset_offset_rbs=12),
    CoresetZeroIndex(index=11, coreset_rbs=48, coreset_ofdm_symbols=1, coreset_offset_rbs=14),
    CoresetZeroIndex(index=12, coreset_rbs=48, coreset_ofdm_symbols=1, coreset_offset_rbs=16),
    CoresetZeroIndex(index=13, coreset_rbs=48, coreset_ofdm_symbols=2, coreset_offset_rbs=12),
    CoresetZeroIndex(index=14, coreset_rbs=48, coreset_ofdm_symbols=2, coreset_offset_rbs=14),
    CoresetZeroIndex(index=15, coreset_rbs=48, coreset_ofdm_symbols=2, coreset_offset_rbs=16),
]

# SCS = 30 kHz, bands with minimal channel bandwidth of 40 MHz
TABLE_13_6 = [
    CoresetZeroIndex(index=0, coreset_rbs=24, coreset_ofdm_symbols=2, coreset_offset_rbs=0),
    CoresetZeroIndex(index=1, coreset_rbs=24, coreset_ofdm_symbols=2, coreset_offset_rbs=4),
    CoresetZeroIndex(index=2, coreset_rbs=24, coreset_ofdm_symbols=3, coreset_offset_rbs=0),
    CoresetZeroIndex(index=3, coreset_rbs=24, coreset_ofdm_symbols=3, coreset_offset_rbs=4),
    CoresetZeroIndex(index=4, coreset_rbs=48, coreset_ofdm_symbols=1, coreset_offset_rbs=0),
    CoresetZeroIndex(index=5, coreset_rbs=48, coreset_ofdm_symbols=1, coreset_offset_rbs=28),
    CoresetZeroIndex(index=6, coreset_rbs=48, coreset_ofdm_symbols=2, coreset_offset_rbs=0),
    CoresetZeroIndex(index=7, coreset_rbs=48, coreset_ofdm_symbols=2, coreset_offset_rbs=28),
    CoresetZeroIndex(index=8, coreset_rbs=48, coreset_ofdm_symbols=3, coreset_offset_rbs=0),
    CoresetZeroIndex(index=9, coreset_rbs=48, coreset_ofdm_symbols=3, coreset_offset_rbs=28),
]

SEARCH_SPACES = {}
SEARCH_SPACES.update(
    dict.fromkeys([(Frequency.from_khz(15), 5), (Frequency.from_khz(15), 10)], TABLE_13_1)
)
SEARCH_SPACES.update(
    dict.fromkeys([(Frequency.from_khz(30), 5), (Frequency.from_khz(30), 10)], TABLE_13_4)
)
SEARCH_SPACES.update(
    dict.fromkeys(
        [
            (Frequency.from_khz(30), 40),
        ],
        TABLE_13_6,
    )
)


def get_coreset_zero_configuration_index(
    band: int, bandwidth: int, subcarrier_spacing: Frequency, offset_to_point_a: int
) -> int:
    """Get CORESET 0 configuration index.

    CORESET 0 configuration index choice criteria are:
    1. Highest possible CORESET 0 bandwidth (coreset_rbs) within the boundaries
       of the overall BWP bandwidth
    2. CORESET 0 offset lower than or equal to OffsetToPointA
    3. Lowest possible number of CORESET 0 OFDM symbols (coreset_ofdm_symbols)

    In case of multiple CORESET 0 configuration indexes matching defined criteria, first one
    from the list will be returned.

    Args:
        band (int): RF band number
        bandwidth (int): BWP bandwidth expressed in the number of RBs (Resource Blocks)
        subcarrier_spacing (Frequency): Subcarrier spacing
        offset_to_point_a (int): OffsetToPointA

    Returns:
        int: CORESET 0 configuration index

    Raises:
        CoresetZeroConfigurationError: If CORESET 0 configuration index can't be determined
    """

    def _bandwidth_and_offset_filter(
        configuration_index: CoresetZeroIndex, coreset_bandwidth
    ) -> bool:
        return (
            configuration_index.coreset_rbs == coreset_bandwidth
            and configuration_index.coreset_offset_rbs <= offset_to_point_a
        )

    logger.debug(
        "Searching for CORESET 0 configuration index for following RF configuration:\n"
        "- band: %s\n"
        "- bandwidth: %s\n"
        "- OffsetToPointA: %s\n",
        band,
        bandwidth,
        offset_to_point_a,
    )
    try:
        search_space = _get_coreset_zero_config_search_space(band, subcarrier_spacing)
        max_coreset_bandwidth = _get_max_possible_coreset_bandwidth(search_space, bandwidth)
        logger.debug("Found CORESET 0 configuration search space")
        candidates = list(
            filter(
                lambda index: _bandwidth_and_offset_filter(index, max_coreset_bandwidth),
                search_space,
            )
        )
        coreset_zero_configuration = min(
            candidates, key=lambda candidate: candidate.coreset_ofdm_symbols
        )
        logger.debug(
            "Found suitable CORESET 0 configuration index: %s", coreset_zero_configuration.index
        )
        return coreset_zero_configuration.index
    except KeyError:
        raise CoresetZeroConfigurationIndexError(
            "Unable to find suitable CORESET 0 configuration search space. "
            "Please check your RF configuration."
        )
    except ValueError:
        raise CoresetZeroConfigurationIndexError(
            "Unable to find CORESET 0 configuration index "
            "for BWP bandwidth = %s and OffsetToPointA = %s. "
            "Please check your RF configuration.",
            bandwidth,
            offset_to_point_a,
        )


def _get_coreset_zero_config_search_space(
    band: int, subcarrier_spacing: Frequency
) -> List[CoresetZeroIndex]:
    """Get CORESET 0 configuration search space for given RF band and SCS.

    Args:
        band (int): RF band number
        subcarrier_spacing (Frequency): Subcarrier spacing

    Returns:
        List[CoresetZeroIndex]: CORESET 0 configuration table defined in
            3GPP TS 38.213 version 17.1.0 Release 17, Chapter 13
    """
    subcarrier_spacing_khz_int = int(subcarrier_spacing / 1000)
    logger.debug(
        "Searching for CORESET 0 configuration search space for following RF configuration:\n"
        "- band: %s\n"
        "- subcarrier spacing: %s kHz\n",
        band,
        subcarrier_spacing_khz_int,
    )
    allowed_channel_bandwidths = ALLOWED_CHANNEL_BANDWIDTHS[band][subcarrier_spacing_khz_int]
    min_allowed_channel_bandwidth = min(allowed_channel_bandwidths)
    return SEARCH_SPACES[(subcarrier_spacing, min_allowed_channel_bandwidth)]


def _get_max_possible_coreset_bandwidth(
    coreset_zero_config_search_space: List[CoresetZeroIndex], bandwidth: int
) -> int:
    candidates = list(
        filter(lambda index: index.coreset_rbs <= bandwidth, coreset_zero_config_search_space)
    )
    return max(candidates, key=lambda index: index.coreset_rbs).coreset_rbs

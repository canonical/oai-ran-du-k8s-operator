# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""ARFCN calculations for different frequencies."""

from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class ARFCNRange:
    """ARFCN range class."""

    lower: float
    upper: float
    freq_grid: float
    freq_offset: float
    arfcn_offset: int


LOW = ARFCNRange(0, 3000, 0.005, 0, 0)
MID = ARFCNRange(3000, 24250, 0.015, 3000, 600000)
HIGH = ARFCNRange(24250, 100000, 0.06, 24250, 2016667)


def freq_to_arfcn(frequency: Union[int, float]) -> Optional[int]:
    """Calculate Absolute Radio Frequency Channel Number (ARFCN).

    Args:
        frequency (float or int): Center frequency in MHz.

    Returns:
        arfcn: int if successful, else None

    Raises:
        ValueError: If the FREQ_GRID is 0 or frequency is out of range.
    """
    if not isinstance(frequency, (int, float)):
        raise TypeError(f"Frequency {frequency} is not a numeric value.")

    ranges = [LOW, MID, HIGH]
    for r in ranges:
        if r.lower <= frequency < r.upper:
            if r.freq_grid == 0:
                raise ValueError("FREQ_GRID cannot be zero.")
            return int(r.arfcn_offset + ((frequency - r.freq_offset) / r.freq_grid))

    raise ValueError(f"Frequency {frequency} is out of supported range.")

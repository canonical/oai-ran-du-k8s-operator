# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Calculate ARFCN for given 5G RF center frequency."""

from dataclasses import dataclass
from decimal import Decimal, getcontext

getcontext().prec = 28
KHZ = Decimal("1000")  # HZ
MHZ = Decimal("1000000")  # HZ


@dataclass
class ARFCNRange:
    """ARFCN range class."""

    lower_frequency: int | Decimal  # HZ
    upper_frequency: int | Decimal  # HZ
    freq_grid: int | Decimal  # HZ
    freq_offset: int | Decimal  # HZ
    arfcn_offset: int


LOW = ARFCNRange(Decimal("0"), Decimal("3000") * MHZ, Decimal("5") * KHZ, 0, 0)
MID = ARFCNRange(
    Decimal("3000") * MHZ,
    Decimal("24250") * MHZ,
    Decimal("15") * KHZ,
    Decimal("3000") * MHZ,
    600000,
)
HIGH = ARFCNRange(
    Decimal("24250") * MHZ,
    Decimal("100000") * MHZ,
    Decimal("60") * KHZ,
    Decimal("24250") * MHZ,
    2016667,
)


def freq_to_arfcn(frequency: int) -> int:
    """Calculate Absolute Radio Frequency Channel Number (ARFCN).

    Args:
        frequency: (int) Center frequency in Hz.

    Returns:
        arfcn: int

    Raises:
        ValueError: If frequency is out of range.
    """
    ranges = [LOW, MID, HIGH]

    frequency = Decimal(frequency)  # type: ignore

    for r in ranges:
        if Decimal(r.lower_frequency) <= frequency < Decimal(r.upper_frequency):
            freq_offset = Decimal(r.freq_offset)
            freq_grid = Decimal(r.freq_grid)
            arfcn_offset = Decimal(r.arfcn_offset)
            return int(arfcn_offset + ((frequency - freq_offset) / freq_grid))

    raise ValueError(
        f"Frequency {frequency} is out of supported range. Supported ranges are: {ranges} Hz"
    )

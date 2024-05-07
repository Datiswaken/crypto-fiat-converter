import csv
from typing import Any

import numpy as np
import polars as pl

from src.fiat_currencies import FiatCurrency


def create_file_total_value(filename: str, value_fiat: float, fiat_currency: FiatCurrency) -> None:
    with open(filename, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["value", "currency"])
        writer.writerow([str(value_fiat), fiat_currency])


def create_file_detailed_values(
    filename: str,
    df: pl.DataFrame,
    values_fiat: np.ndarray[float, np.dtype[Any]],
    fiat_currency: FiatCurrency
) -> None:
    df = df.with_columns(
        [
            (pl.Series(name="value_fiat", values=values_fiat)),
            (pl.Series(name="currency", values=[fiat_currency]))
        ]
    )
    df.write_csv(filename)

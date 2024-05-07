#!/usr/bin/env python3

import sys
import argparse
from datetime import datetime

import numpy as np
import polars as pl

from src.conversion_type import convert_for_date_range
from src.container import Container
from src.lib.input_validation import is_output_filename_valid
from src.fiat_currencies import FiatCurrency
from src.util import find_nearest_date
from src.output import create_file_total_value, create_file_detailed_values

INPUT_FILE_REQUIRED_COLUMNS = ["date", "coin", "amount"]


def convert_by_file(
        input_file: str,
        convert_to: FiatCurrency = FiatCurrency.USD,
        output_filename: str = "output.csv",
) -> None:
    container = Container()
    try:
        df = pl.read_csv(
            source=input_file,
            separator=",",
            columns=INPUT_FILE_REQUIRED_COLUMNS,
            try_parse_dates=True,
            dtypes={"date": pl.Datetime}
        )
    except pl.ColumnNotFoundError as exc:
        print(f"{exc}")
        sys.exit("Exiting program")
    except Exception as exc:
        print(f"Failed to load input file: {exc}")
        sys.exit("Exiting program")

    if df["date"].dtype != pl.Datetime:
        print(f"Could not parse all dates. Please re-check the format.")
        sys.exit("Exiting program")

    df = df.sort(by="date")
    min_date = df.select(pl.first("date")).to_series()[0].replace(hour=0, minute=0, second=0, microsecond=0)
    max_date = df.select(pl.last("date")).to_series()[0].replace(hour=23, minute=59, second=59, microsecond=0)
    if len(df["coin"].value_counts()) > 1:
        print("More than one coin/token found in data.")
        sys.exit("Exiting program")
    convert_from = df["coin"].unique()[0]

    historical_data = convert_for_date_range(
        api_adapter=container.coingecko_api_adapter(),
        start_date=min_date,
        end_date=max_date,
        convert_from=convert_from,
        convert_to=convert_to
    )
    timestamps = [data_point[0] for data_point in historical_data["prices"]]

    nearest_dates = [find_nearest_date(timestamps=timestamps, pivot=int(dt.timestamp()) * 1000) for dt in df["date"]]
    prices_at_dates = np.zeros(len(nearest_dates))
    for idx, nearest_date in enumerate(nearest_dates):
        for data_point in historical_data["prices"]:
            if data_point[0] == nearest_date:
                prices_at_dates[idx] = data_point[1]

    amounts = df["amount"].to_numpy()
    values_fiat = np.multiply(prices_at_dates, amounts)
    total_value_fiat = np.sum(values_fiat)

    current_time = datetime.now().strftime("%Y%m%dT%H%M%S")
    output_filename_split = output_filename.split(".")
    output_filename_total = f"{output_filename_split[0]}_{current_time}.{output_filename_split[1]}"
    output_filename_details = f"{output_filename_split[0]}_details_{current_time}.{output_filename_split[1]}"

    create_file_total_value(
        filename=output_filename_total,
        value_fiat=total_value_fiat,
        fiat_currency=FiatCurrency(convert_to)
    )
    create_file_detailed_values(
        filename=output_filename_details,
        df=df,
        values_fiat=values_fiat,
        fiat_currency=FiatCurrency(convert_to)
    )

    print(f"Everything done! Files created: {output_filename_total} & {output_filename_details}")


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file")
    parser.add_argument("-c", "--convert-to")
    parser.add_argument("-o", "--output-filename", default="output.csv")
    args = parser.parse_args()

    if args.file is not None:
        if args.convert_to:
            convert_to = FiatCurrency(args.convert_to)
        else:
            convert_to = FiatCurrency.USD

        if not is_output_filename_valid(filename=args.output_filename):
            print(f"Invalid filename: {args.output_filename}. Must end on '.csv' and contain not more than one '.'")
            sys.exit("Exiting program")
        convert_by_file(input_file=args.file, convert_to=convert_to, output_filename=args.output_filename)


if __name__ == "__main__":
    run()

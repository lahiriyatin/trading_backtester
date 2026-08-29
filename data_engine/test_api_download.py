from data_engine.loader import (
    TwelveDataError,
    fetch_time_series,
    save_raw_data,
)


def main() -> None:
    symbol = "EUR/USD"
    interval = "1min"

    print(f"Requesting sample data for {symbol}...")

    try:
        dataframe, metadata = fetch_time_series(
            symbol=symbol,
            interval=interval,
            outputsize=100,
        )
    except TwelveDataError as error:
        print(f"Download failed: {error}")
        return

    print("\nMetadata:")
    print(metadata)

    print("\nData types:")
    print(dataframe.dtypes)

    print("\nFirst five candles:")
    print(dataframe.head().to_string(index=False))

    print("\nLast five candles:")
    print(dataframe.tail().to_string(index=False))

    print(f"\nRows: {len(dataframe)}")
    print(f"Start: {dataframe['timestamp'].min()}")
    print(f"End: {dataframe['timestamp'].max()}")
    print(f"Duplicate timestamps: {dataframe['timestamp'].duplicated().sum()}")
    print(f"Missing timestamps: {dataframe['timestamp'].isna().sum()}")

    output_path = save_raw_data(
        dataframe=dataframe,
        symbol=symbol,
        interval=interval,
    )

    print(f"\nSaved sample: {output_path}")


if __name__ == "__main__":
    main()

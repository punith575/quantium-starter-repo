import pandas as pd
from pathlib import Path

def main():
    data_dir = Path("data")
    files = [
        data_dir / "daily_sales_data_0.csv",
        data_dir / "daily_sales_data_1.csv",
        data_dir / "daily_sales_data_2.csv",
    ]

    df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
    df.columns = [c.strip().lower() for c in df.columns]

    # Clean product (handles odd spaces)
    df["product"] = (
        df["product"]
        .astype(str)
        .str.replace("\u00a0", " ", regex=False)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
    )

    print("TOP PRODUCTS:")
    print(df["product"].value_counts().head(10))

    # Filter only pink morsel
    df = df[df["product"].eq("pink morsel")].copy()
    print("AFTER PRODUCT FILTER:", len(df))

    # Clean numeric fields (handles "$", commas, etc.)
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

    # price might be like "$12.34" or "1,234.56"
    df["price"] = (
        df["price"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    print("NULL quantity:", int(df["quantity"].isna().sum()))
    print("NULL price:", int(df["price"].isna().sum()))

    # Drop rows where numeric conversion failed
    df = df.dropna(subset=["quantity", "price"])
    print("AFTER NUMERIC CLEAN:", len(df))

    # Sales
    df["Sales"] = df["quantity"] * df["price"]

    # Output
    out = df[["Sales", "date", "region"]].rename(
        columns={"date": "Date", "region": "Region"}
    )

    out_file = Path("output_sales.csv")
    out.to_csv(out_file, index=False)

    print(f"Created {out_file} with {len(out)} rows")

if __name__ == "__main__":
    main()

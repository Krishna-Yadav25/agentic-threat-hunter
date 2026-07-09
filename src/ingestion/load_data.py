import pandas as pd
import os

# Paths
RAW_DATA_PATH = "data/raw/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"
SAMPLE_DATA_PATH = "data/sample/sample_logs.csv"


def load_data(path: str) -> pd.DataFrame:
    
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df


def explore_data(df: pd.DataFrame):

    print("Shape (rows, columns):", df.shape)
    print("\nColumns:\n", list(df.columns))
    print("\nLabel counts:\n", df["Label"].value_counts())
    print("\nFirst 5 rows:\n", df.head())


def save_sample(df: pd.DataFrame, path: str, n: int = 200):
  
    sample = df.sample(n=min(n, len(df)), random_state=42)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sample.to_csv(path, index=False)
    print(f"\nSample of {len(sample)} rows saved to {path}")


if __name__ == "__main__":
    df = load_data(RAW_DATA_PATH)
    explore_data(df)
    save_sample(df, SAMPLE_DATA_PATH)
import pandas as pd

RAW_DATA_PATH = "data/raw/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"
_df = pd.read_csv(RAW_DATA_PATH)
_df.columns = _df.columns.str.strip()


def get_events_by_port(port: int, limit: int = 10) -> str:
    matches = _df[_df["Destination Port"] == port].head(limit)
    if matches.empty:
        return f"No events found for port {port}."

    lines = [f"Found {len(_df[_df['Destination Port'] == port])} total events for port {port}. Showing first {limit}:"]
    for idx, row in matches.iterrows():
        lines.append(
            f"Row {idx}: Flow Duration={row['Flow Duration']}, "
            f"Fwd Packets={row['Total Fwd Packets']}, "
            f"Bwd Packets={row['Total Backward Packets']}, "
            f"Label={row['Label']}"
        )
    return "\n".join(lines)


def get_summary_stats() -> str:
    total = len(_df)
    label_counts = _df["Label"].value_counts().to_dict()
    lines = [f"Total events in dataset: {total}"]
    for label, count in label_counts.items():
        lines.append(f"  {label}: {count} events")
    return "\n".join(lines)


def get_events_by_label(label: str, limit: int = 10) -> str:
    matches = _df[_df["Label"] == label].head(limit)
    if matches.empty:
        return f"No events found with label '{label}'."

    lines = [f"Found {len(_df[_df['Label'] == label])} total events with label '{label}'. Showing first {limit}:"]
    for idx, row in matches.iterrows():
        lines.append(
            f"Row {idx}: Dest Port={row['Destination Port']}, "
            f"Flow Duration={row['Flow Duration']}, "
            f"Fwd Packets={row['Total Fwd Packets']}"
        )
    return "\n".join(lines)
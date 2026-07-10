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


def compare_traffic_patterns(port: int = None) -> str:
    subset = _df if port is None else _df[_df["Destination Port"] == port]

    if subset.empty:
        return f"No events found for port {port}."

    lines = [f"Traffic pattern comparison" + (f" for port {port}" if port else "") + ":"]

    for label in subset["Label"].unique():
        label_data = subset[subset["Label"] == label]
        lines.append(f"\nLabel: {label} ({len(label_data)} events)")
        lines.append(f"  Avg Flow Duration: {label_data['Flow Duration'].mean():.2f}")
        lines.append(f"  Avg Flow Packets/s: {label_data['Flow Packets/s'].mean():.2f}")
        lines.append(f"  Avg Fwd Packets: {label_data['Total Fwd Packets'].mean():.2f}")
        lines.append(f"  Avg Bwd Packets: {label_data['Total Backward Packets'].mean():.2f}")
        lines.append(f"  Avg SYN Flag Count: {label_data['SYN Flag Count'].mean():.2f}")
        lines.append(f"  Avg ACK Flag Count: {label_data['ACK Flag Count'].mean():.2f}")

    return "\n".join(lines)


def get_flow_rate_outliers(port: int = None, top_n: int = 10) -> str:
  
    subset = _df if port is None else _df[_df["Destination Port"] == port]

    if subset.empty:
        return f"No events found for port {port}."

    top_events = subset.nlargest(top_n, "Flow Packets/s")

    lines = [f"Top {top_n} events by Flow Packets/s (highest traffic rate):"]
    for idx, row in top_events.iterrows():
        lines.append(
            f"Row {idx}: Dest Port={row['Destination Port']}, "
            f"Flow Packets/s={row['Flow Packets/s']:.2f}, "
            f"Flow Duration={row['Flow Duration']}, "
            f"Label={row['Label']}"
        )
    return "\n".join(lines)
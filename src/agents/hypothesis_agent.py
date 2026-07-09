import sys
import os
import pandas as pd
from openai import OpenAI


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import GROQ_API_KEY

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

SAMPLE_PATH = "data/sample/sample_logs.csv"


def logs_to_text(df: pd.DataFrame, n: int = 15) -> str:
    """DataFrame ke rows ko readable text me convert karta hai LLM ke liye."""
    subset = df.head(n)
    lines = []
    for idx, row in subset.iterrows():
        lines.append(
            f"Row {idx}: Dest Port={row.get('Destination Port')}, "
            f"Flow Duration={row.get('Flow Duration')}, "
            f"Fwd Packets={row.get('Total Fwd Packets')}, "
            f"Bwd Packets={row.get('Total Backward Packets')}, "
            f"Label={row.get('Label')}"
        )
    return "\n".join(lines)


def ask_llm_for_hypothesis(log_text: str) -> str:
    prompt = f"""You are a cybersecurity threat hunting analyst. Below are network flow log entries.

{log_text}

Based on these logs, do you see any patterns that look suspicious or indicative of an attack (e.g., DDoS, port scanning, unusual traffic volume)? 
Give a short hypothesis (2-4 sentences) about what might be happening, and mention which rows caught your attention and why."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    df = pd.read_csv(SAMPLE_PATH)
    df.columns = df.columns.str.strip()

    log_text = logs_to_text(df)
    print("=== Logs Sent to LLM ===")
    print(log_text)

    print("\n=== LLM Hypothesis ===")
    hypothesis = ask_llm_for_hypothesis(log_text)
    print(hypothesis)
import sys
import os
import pandas as pd
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import GROQ_API_KEY

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

SAMPLE_PATH = "data/sample/sample_logs.csv"


def logs_to_text(df: pd.DataFrame, n: int = 15) -> str:
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


def generate_hypothesis(log_text: str) -> str:
   
    prompt = f"""You are a cybersecurity threat hunting analyst. Below are network flow log entries.

{log_text}

Carefully analyze these logs. Do NOT assume there is an attack — many logs represent completely normal traffic. 
Only flag something as suspicious if there is clear statistical evidence (e.g., abnormal packet ratios, unusually 
short flow durations combined with high packet counts, repeated identical patterns suggesting automation).

If the traffic looks like normal, everyday usage (varied ports, reasonable flow durations, balanced packet ratios), 
explicitly state that no strong indicators of an attack were found.

Give a short assessment (2-4 sentences) stating either:
(a) a specific hypothesis about suspicious activity, with which rows caught your attention and why, or
(b) that the traffic appears normal, with a brief justification."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=500,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def run_hypothesis_agent(sample_path: str = SAMPLE_PATH) -> str:
    df = pd.read_csv(sample_path)
    df.columns = df.columns.str.strip()

    log_text = logs_to_text(df)
    hypothesis = generate_hypothesis(log_text)
    return hypothesis


if __name__ == "__main__":
    print("=== Logs Sent to LLM ===")
    df = pd.read_csv(SAMPLE_PATH)
    df.columns = df.columns.str.strip()
    print(logs_to_text(df))

    print("\n=== LLM Hypothesis ===")
    hypothesis = run_hypothesis_agent()
    print(hypothesis)
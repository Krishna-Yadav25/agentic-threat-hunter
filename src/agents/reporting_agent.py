import sys
import os
from datetime import datetime
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import GROQ_API_KEY

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

REPORTS_DIR = "outputs/reports"


def generate_report_content(hypothesis: str, verdict: str) -> str:
    prompt = f"""You are a cybersecurity analyst writing a formal incident report for a SOC team.

Below is the hypothesis generated during initial threat hunting, and the verdict from the investigation phase.

HYPOTHESIS:
{hypothesis}

INVESTIGATION VERDICT:
{verdict}

Write a clear, professional incident report in Markdown format with these sections:
1. Executive Summary (2-3 sentences, non-technical, for management)
2. Detection Details (what triggered the hunt, what was observed)
3. Investigation Findings (what evidence was gathered)
4. Verdict & Confidence
5. Recommended Actions (2-4 concrete next steps for the SOC team)

Keep it concise and professional. Use Markdown headers (##) for each section."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def save_report(report_content: str, report_dir: str = REPORTS_DIR) -> str:
    os.makedirs(report_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"incident_report_{timestamp}.md"
    filepath = os.path.join(report_dir, filename)

    full_content = f"# Threat Hunting Incident Report\n\n"
    full_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    full_content += "---\n\n"
    full_content += report_content

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    return filepath


def run_reporting_agent(hypothesis: str, verdict: str) -> str:
    report_content = generate_report_content(hypothesis, verdict)
    filepath = save_report(report_content)
    return filepath


if __name__ == "__main__":
    sample_hypothesis = (
        "Multiple flows targeting destination port 80 show a pattern of low forward "
        "packet counts and uneven forward-to-backward packet ratios, suggesting a "
        "potential DDoS attack against the target server."
    )
    sample_verdict = (
        "VERDICT: MALICIOUS\n"
        "CONFIDENCE: HIGH\n"
        "REASONING: The traffic patterns show a significant difference in average "
        "forward packet counts and forward-to-backward ratios between BENIGN and DDoS "
        "labels. Flow rate outliers analysis also confirms abnormally high packet rates "
        "consistent with a DDoS attack."
    )

    print("=== Generating Report ===")
    filepath = run_reporting_agent(sample_hypothesis, sample_verdict)
    print(f"Report saved to: {filepath}")
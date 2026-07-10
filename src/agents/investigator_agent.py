import sys
import os
import json
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import GROQ_API_KEY
from tools.log_query_tools import (
    get_events_by_port,
    get_summary_stats,
    get_events_by_label,
    compare_traffic_patterns,
    get_flow_rate_outliers,
)

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_events_by_port",
            "description": "Get network events filtered by a specific destination port",
            "parameters": {
                "type": "object",
                "properties": {
                    "port": {"type": "integer", "description": "The destination port to filter by"},
                    "limit": {"type": "integer", "description": "Max number of events to return", "default": 10}
                },
                "required": ["port"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_summary_stats",
            "description": "Get overall summary statistics of the dataset (total events, label counts)",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_events_by_label",
            "description": "Get network events filtered by label (e.g. 'DDoS' or 'BENIGN')",
            "parameters": {
                "type": "object",
                "properties": {
                    "label": {"type": "string", "description": "The label to filter by"},
                    "limit": {"type": "integer", "description": "Max number of events to return", "default": 10}
                },
                "required": ["label"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_traffic_patterns",
            "description": (
                "Compare statistical traffic patterns (packet rate, SYN/ACK flag counts, "
                "flow duration) between different labels (DDoS vs BENIGN). Very useful for "
                "confirming or refuting an attack hypothesis based on traffic behavior. "
                "Optionally filter by destination port."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "port": {"type": "integer", "description": "Optional destination port to filter by"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_flow_rate_outliers",
            "description": (
                "Get events with the highest packet rate (Flow Packets/s). Abnormally high "
                "rates are strong evidence of flood/DDoS attacks. Optionally filter by port."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "port": {"type": "integer", "description": "Optional destination port to filter by"},
                    "top_n": {"type": "integer", "description": "Number of top events to return", "default": 10}
                },
                "required": []
            }
        }
    }
]

AVAILABLE_TOOLS = {
    "get_events_by_port": get_events_by_port,
    "get_summary_stats": get_summary_stats,
    "get_events_by_label": get_events_by_label,
    "compare_traffic_patterns": compare_traffic_patterns,
    "get_flow_rate_outliers": get_flow_rate_outliers,
}


def run_investigation(hypothesis: str, max_turns: int = 8) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a cybersecurity investigator agent. You have been given a hypothesis "
                "from another analyst. Use the available tools to investigate and gather evidence. "
                "Note: this dataset does NOT contain source/destination IP addresses, so base your "
                "investigation on statistical traffic patterns instead — packet rates, SYN/ACK flag "
                "counts, flow duration, and packet count ratios. Use compare_traffic_patterns and "
                "get_flow_rate_outliers to gather strong statistical evidence. "
                "Once you have enough evidence, give a final verdict in this format:\n"
                "VERDICT: [MALICIOUS/BENIGN/INCONCLUSIVE]\n"
                "CONFIDENCE: [LOW/MEDIUM/HIGH]\n"
                "REASONING: [your explanation]"
            )
        },
        {"role": "user", "content": f"Hypothesis to investigate: {hypothesis}"}
    ]

    consecutive_failures = 0

    for turn in range(max_turns):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=TOOLS_SCHEMA,
                max_tokens=800,
                temperature=0
            )
        except Exception as e:
            consecutive_failures += 1
            print(f"[Turn {turn + 1}] Tool call failed ({e}). Retrying...")
            if consecutive_failures >= 2:
                return "Investigation stopped: repeated tool-calling errors from the model."
            messages.append({
                "role": "user",
                "content": "Your last response was not in the correct tool calling format. Please try again using a valid tool call."
            })
            continue

        consecutive_failures = 0
        msg = response.choices[0].message

        if not msg.tool_calls:
            print(f"\n[Turn {turn + 1}] Final answer received.")
            return msg.content

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [tc.model_dump() for tc in msg.tool_calls]
        })

        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name

            try:
                fn_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                fn_args = {}

            print(f"[Turn {turn + 1}] Agent calling tool: {fn_name}({fn_args})")

            if fn_name in AVAILABLE_TOOLS:
                try:
                    result = AVAILABLE_TOOLS[fn_name](**fn_args)
                except Exception as e:
                    result = f"Error while running tool '{fn_name}': {e}"
            else:
                result = f"Error: tool '{fn_name}' not found."

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    return "Investigation stopped: max turns reached without a final verdict."


if __name__ == "__main__":
    sample_hypothesis = (
        "Multiple flows targeting destination port 80 show a pattern of low forward "
        "packet counts and uneven forward-to-backward packet ratios, suggesting a "
        "potential DDoS attack against the target server."
    )

    print("=== Starting Investigation ===")
    print(f"Hypothesis: {sample_hypothesis}\n")

    verdict = run_investigation(sample_hypothesis)

    print("\n=== Final Verdict ===")
    print(verdict)
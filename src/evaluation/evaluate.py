import sys
import os
import pandas as pd
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import GROQ_API_KEY
from agents.hypothesis_agent import run_hypothesis_agent

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

RAW_DATA_PATH = "data/raw/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"
TEMP_SAMPLE_PATH = "data/sample/eval_temp_sample.csv"
RESULTS_PATH = "outputs/evaluation_results.csv"

NUM_SAMPLES_PER_CLASS = 5   
ROWS_PER_SAMPLE = 15        

def build_test_samples(df: pd.DataFrame) -> list:
    """
    Test samples banata hai: kuch mostly-DDoS, kuch mostly-BENIGN.
    Har sample ek dict return karta hai jisme rows aur true_label hota hai.
    """
    samples = []
    ddos_rows = df[df["Label"] == "DDoS"]
    benign_rows = df[df["Label"] == "BENIGN"]

    for i in range(NUM_SAMPLES_PER_CLASS):
        batch = ddos_rows.sample(n=min(ROWS_PER_SAMPLE, len(ddos_rows)), random_state=i)
        samples.append({"data": batch, "true_label": "SUSPICIOUS"})

    for i in range(NUM_SAMPLES_PER_CLASS):
        batch = benign_rows.sample(n=min(ROWS_PER_SAMPLE, len(benign_rows)), random_state=i + 100)
        samples.append({"data": batch, "true_label": "NORMAL"})

    return samples


def classify_hypothesis(hypothesis_text: str) -> str:
    prompt = f"""Below is a threat analyst's assessment of some network logs.

{hypothesis_text}

Does this assessment conclude that the traffic is SUSPICIOUS (a specific attack pattern was identified with 
supporting evidence) or NORMAL (no strong attack indicators were found, or the analyst explicitly said traffic looks normal)?

Respond with exactly one word: SUSPICIOUS or NORMAL."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=10,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content.strip().upper()
    return "SUSPICIOUS" if "SUSPICIOUS" in answer else "NORMAL"


def run_evaluation():
    print("Loading dataset...")
    df = pd.read_csv(RAW_DATA_PATH)
    df.columns = df.columns.str.strip()

    print("Building test samples...")
    samples = build_test_samples(df)

    results = []

    for i, sample in enumerate(samples):
        print(f"\n[{i + 1}/{len(samples)}] Testing sample (true label: {sample['true_label']})...")

        sample["data"].to_csv(TEMP_SAMPLE_PATH, index=False)

        
        hypothesis = run_hypothesis_agent(sample_path=TEMP_SAMPLE_PATH)

        predicted_label = classify_hypothesis(hypothesis)

        correct = predicted_label == sample["true_label"]
        print(f"  True: {sample['true_label']} | Predicted: {predicted_label} | {'✓ Correct' if correct else '✗ Wrong'}")

        results.append({
            "sample_id": i + 1,
            "true_label": sample["true_label"],
            "predicted_label": predicted_label,
            "correct": correct,
            "hypothesis": hypothesis
        })

    
    if os.path.exists(TEMP_SAMPLE_PATH):
        os.remove(TEMP_SAMPLE_PATH)

    results_df = pd.DataFrame(results)

    os.makedirs("outputs", exist_ok=True)
    results_df.to_csv(RESULTS_PATH, index=False)
    accuracy = results_df["correct"].mean() * 100
    total = len(results_df)
    correct_count = results_df["correct"].sum()

    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Total samples tested: {total}")
    print(f"Correct predictions: {correct_count}")
    print(f"Accuracy: {accuracy:.2f}%")

    print("\nConfusion Matrix:")
    confusion = pd.crosstab(results_df["true_label"], results_df["predicted_label"],
                             rownames=["True"], colnames=["Predicted"])
    print(confusion)

    print(f"\nDetailed results saved to: {RESULTS_PATH}")

    return results_df


if __name__ == "__main__":
    run_evaluation()
# 🛡️ Agentic AI for Automated Threat Hunting

An autonomous multi-agent system that performs threat hunting on network logs — inspired by how a real SOC analyst investigates suspicious activity, but automated using LLM-based agents.

## 📌 Overview

Traditional threat hunting is manual and slow. This project builds an **agentic AI pipeline** that:
- Ingests network traffic logs
- Forms hypotheses about potential threats
- Investigates by querying and correlating log data
- Cross-references findings with threat intelligence
- Generates a human-readable incident report with a verdict

## 🏗️ Architecture
Log Ingestion → Hypothesis Agent → Investigator Agent → Threat Intel Agent → Reporting Agent

## 🛠️ Tech Stack

- **Python 3.11**
- **LangGraph** — multi-agent orchestration
- **Anthropic Claude API** — LLM reasoning
- **Pandas** — log processing
- **Streamlit** — dashboard/UI
- **Dataset**: [CICIDS2017](https://www.unb.ca/cic/datasets/ids-2017.html)

## 📂 Project Structure

```
agentic-threat-hunter/
├── data/
│   ├── raw/           # original dataset (not tracked in git)
│   ├── processed/     # cleaned data
│   └── sample/        # small sample for quick testing
├── src/
│   ├── ingestion/      # data loading and normalization
│   ├── agents/         # hypothesis, investigator, threat intel, reporting agents
│   ├── tools/           # log query tools, intel lookup tools
│   ├── orchestrator/  # LangGraph pipeline
│   └── utils/            # config, logging
├── dashboard/          # Streamlit UI
├── notebooks/          # exploration notebooks
└── outputs/reports/    # generated incident reports
```

## 🚀 Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd agentic-threat-hunter
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell
```

### 3. Install dependencies
```bash
pip install -r requirement.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
ANTHROPIC_API_KEY=your_api_key_here

### 5. Download the dataset
Download `MachineLearningCSV.zip` from [CICIDS2017](https://www.unb.ca/cic/datasets/ids-2017.html) and place a CSV file inside `data/raw/`.

### 6. Run data ingestion
```bash
python src/ingestion/load_data.py
```

## 📊 Current Progress

- [x] Project setup & folder structure
- [x] Dataset ingestion pipeline
- [ ] Hypothesis agent (LLM-based anomaly detection)
- [ ] Investigator agent with log query tools
- [ ] Threat intelligence integration
- [ ] Reporting agent + incident summaries
- [ ] Streamlit dashboard

## 📄 License

This project is for educational purposes.

## 🙏 Acknowledgments

Dataset: Sharafaldin, I., Lashkari, A.H., Ghorbani, A.A., "Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization", ICISSP 2018.
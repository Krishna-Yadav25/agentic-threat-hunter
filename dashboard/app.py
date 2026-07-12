import sys
import os
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.orchestrator.graph import run_pipeline


st.set_page_config(
    page_title="Agentic Threat Hunter",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Agentic AI Threat Hunter")
st.caption("Autonomous multi-agent threat hunting pipeline — Hypothesis → Investigation → Report")

st.divider()
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None

col1, col2 = st.columns([1, 4])
with col1:
    run_button = st.button("🔍 Run Threat Hunt", type="primary", use_container_width=True)

if run_button:
    with st.spinner("Running Hypothesis Agent..."):
        pass  
    with st.status("Agentic pipeline running...", expanded=True) as status:
        st.write("🧠 Hypothesis Agent analyzing sample logs...")
        result = run_pipeline()
        st.write("🔎 Investigator Agent gathering evidence...")
        st.write("📄 Reporting Agent generating incident report...")
        status.update(label="Pipeline complete!", state="complete", expanded=False)

    st.session_state.pipeline_result = result

if st.session_state.pipeline_result:
    result = st.session_state.pipeline_result

    st.divider()
    st.subheader("📋 Results")

    tab1, tab2, tab3 = st.tabs(["🧠 Hypothesis", "🔎 Investigation Verdict", "📄 Full Report"])

    with tab1:
        st.markdown(result["hypothesis"])

    with tab2:
        verdict_text = result["verdict"]
        if "MALICIOUS" in verdict_text.upper():
            st.error("⚠️ VERDICT: MALICIOUS")
        elif "BENIGN" in verdict_text.upper():
            st.success("✅ VERDICT: BENIGN")
        else:
            st.warning("❓ VERDICT: INCONCLUSIVE")

        st.markdown(verdict_text)

    with tab3:
        report_path = result["report_path"]
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                report_content = f.read()
            st.markdown(report_content)

            st.download_button(
                label="⬇️ Download Report",
                data=report_content,
                file_name=os.path.basename(report_path),
                mime="text/markdown"
            )
        else:
            st.warning("Report file not found.")

else:
    st.info("👆 Click 'Run Threat Hunt' to start the agentic pipeline.")

st.divider()
st.caption("Powered by LangGraph + Groq (Llama 3.3 70B) | Dataset: CICIDS2017")
import os
import json
import uuid
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI
from prompts import TRIAGE_SYSTEM_PROMPT

# -------------------------------
# Page Config & Env
# -------------------------------
st.set_page_config(
    page_title="Customer Feedback Triage System",
    page_icon="🤖",
    layout="wide"
)

load_dotenv()

# -------------------------------
# Azure Client
# -------------------------------
@st.cache_resource
def get_azure_client():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    if not endpoint or not key or not deployment:
        return None, None

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=key,
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
    return client, deployment


client, DEPLOYMENT_NAME = get_azure_client()

# -------------------------------
# Rule-Based Classifier
# -------------------------------
class RuleBasedClassifier:
    def classify(self, text):
        text_lower = text.lower()

        if any(x in text_lower for x in ["crash", "error", "bug", "broken", "slow"]):
            category = "Complaint"
        elif any(x in text_lower for x in ["add", "feature", "improve"]):
            category = "Feature Request"
        elif any(x in text_lower for x in ["love", "great", "good", "awesome"]):
            category = "Praise"
        elif "?" in text_lower:
            category = "Question"
        else:
            category = "Question"

        if any(x in text_lower for x in ["immediately", "urgent", "crash"]):
            urgency = "High"
        elif category == "Praise":
            urgency = "Low"
        else:
            urgency = "Medium"

        if urgency == "High":
            action = "Escalate"
        elif category == "Feature Request":
            action = "Forward"
        elif category == "Praise":
            action = "Ignore"
        else:
            action = "Respond"

        return {
            "Category": category,
            "Urgency": urgency,
            "Suggested Action": action,
            "Reasoning": "Baseline logic using keyword rules.",
            "meta": {"cost_usd": 0.0}
        }


# -------------------------------
# AI Classifier
# -------------------------------
class AIClassifier:
    def classify(self, text):
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Feedback: {text}"}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        usage = response.usage

        result["meta"] = {
            "tokens": usage.total_tokens if usage else 0,
            "cost_usd": 0.0
        }
        return result


# -------------------------------
# File Reader
# -------------------------------
def read_uploaded_file(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        col = "feedback" if "feedback" in df.columns else df.columns[0]
        return df[col].dropna().tolist()
    else:
        content = uploaded_file.getvalue().decode("utf-8")
        return [line.strip() for line in content.splitlines() if line.strip()]


# -------------------------------
# Streamlit UI
# -------------------------------
def main():
    st.title("🤖 Customer Feedback Triage System")
    st.write("Compare **Azure OpenAI decisions** with a **rule-based baseline**.")

    with st.sidebar:
        st.subheader("System Status")
        st.success("Azure Connected" if client else "Azure Not Connected")

    uploaded_file = st.file_uploader("Upload feedback file", ["txt", "csv"])

    if uploaded_file and st.button("🚀 Start Analysis"):
        batch_id = uuid.uuid4().hex[:8].upper()
        st.success(f"Batch ID: {batch_id}")

        feedback_list = read_uploaded_file(uploaded_file)

        ai = AIClassifier()
        rules = RuleBasedClassifier()

        results = []

        for idx, text in enumerate(feedback_list, start=1):
            ai_res = ai.classify(text)
            rule_res = rules.classify(text)

            results.append({
                "id": idx,
                "feedback": text,
                "ai_decision": ai_res,
                "baseline_decision": rule_res,
                "comparison": {
                    "category_match": ai_res["Category"] == rule_res["Category"],
                    "urgency_match": ai_res["Urgency"] == rule_res["Urgency"],
                    "action_match": ai_res["Suggested Action"] == rule_res["Suggested Action"]
                }
            })

        st.subheader("📊 Results")
        df = pd.DataFrame([
            {
                "Feedback": r["feedback"],
                "AI Category": r["ai_decision"]["Category"],
                "Rule Category": r["baseline_decision"]["Category"],
                "Category Match": r["comparison"]["category_match"]
            } for r in results
        ])
        st.dataframe(df, use_container_width=True)

        json_data = json.dumps(results, indent=4)
        st.download_button(
            "💾 Download JSON Output",
            json_data,
            file_name=f"triage_output_{batch_id}.json",
            mime="application/json"
        )


if __name__ == "__main__":
    main()

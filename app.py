import streamlit as st
from streamlit_chat import message
from groq import Groq
import os
from dotenv import load_dotenv
import time
import requests
from fpdf import FPDF

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
jooble_api_key = os.getenv("JOOBLE_API_KEY")

# GROQ client setup
client = Groq(api_key=groq_api_key)

# Streamlit config
st.set_page_config(page_title="Hiring Partner AI", page_icon="🤝", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .stChatInputContainer {
        background: #fff;
        border-top: 2px solid #ccc;
    }
    .stButton button {
        background-color: #003366;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("## 🤝 Hiring Partner Assistant")
st.caption("Smarter hiring through intelligent conversations.")

# Session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "stage" not in st.session_state:
    st.session_state.stage = "greeting"
if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {}
if "tech_questions" not in st.session_state:
    st.session_state.tech_questions = []
if "code_questions" not in st.session_state:
    st.session_state.code_questions = []
if "job_recommendations" not in st.session_state:
    st.session_state.job_recommendations = []
if "end_chat" not in st.session_state:
    st.session_state.end_chat = False

# Generate LLM response
def generate_llm_response(prompt):
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"

# Technical questions
def get_technical_questions(tech_stack):
    prompt = f"""You are an AI recruiter. Generate 3 concise technical interview questions EACH for the following technologies:\n{tech_stack}."""
    return generate_llm_response(prompt)

# High-level coding questions
def get_coding_questions(tech_stack):
    prompt = f"""As a senior AI interviewer, suggest 3 challenging coding questions based on the following tech stack:\n{tech_stack}."""
    return generate_llm_response(prompt)

# Job recommendations from Jooble API
def get_job_recommendations(position, location, remote=True):
    url = "https://jooble.org/api/"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "keywords": position,
        "location": location,
        "remote": remote
    }

    try:
        response = requests.post(f"{url}{jooble_api_key}", json=payload, headers=headers)
        if response.status_code == 200:
            job_data = response.json()
            jobs = job_data.get('jobs', []) or job_data.get('results', [])
            if not jobs:
                return ["⚠️ No jobs found for the provided position and location."]
            formatted = []
            for job in jobs[:5]:
                title = job.get('title', 'No title')
                location = job.get('location', 'N/A')
                link = job.get('link', '#')
                formatted.append(f"🔹 **{title}**\n📍 {location}\n🔗 [Apply Here]({link})")
            return formatted
        else:
            return [f"⚠️ Jooble API returned status {response.status_code}: {response.text}"]
    except Exception as e:
        return [f"⚠️ Error while fetching jobs: {str(e)}"]

# PDF Export
def export_pdf(candidate_info, tech_qs, code_qs, job_recs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Hiring Partner - Candidate Summary", ln=True, align='C')
    pdf.ln(10)

    for key, val in candidate_info.items():
        pdf.multi_cell(0, 10, f"{key}: {val}")

    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, "Technical Questions", ln=True)
    pdf.set_font("Arial", size=12)
    for q in tech_qs:
        pdf.multi_cell(0, 10, f"- {q}")

    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, "Coding Questions", ln=True)
    pdf.set_font("Arial", size=12)
    for q in code_qs:
        pdf.multi_cell(0, 10, f"- {q}")

    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, "Recommended Jobs", ln=True)
    pdf.set_font("Arial", size=12)
    for job in job_recs:
        pdf.multi_cell(0, 10, job.replace("🔹", "-").replace("📍", "Location:"))

    pdf_path = "/tmp/candidate_summary.pdf"
    pdf.output(pdf_path)
    return pdf_path

# Chat logic
def chat_logic(user_input):
    info = st.session_state.candidate_info
    stage = st.session_state.stage

    if user_input.lower() in ["exit", "quit", "bye", "end"]:
        st.session_state.end_chat = True
        return "✅ Thank you for chatting with Hiring Partner! We’ll be in touch shortly. Goodbye! 👋"

    if stage == "greeting":
        st.session_state.stage = "full_name"
        return "👋 Welcome! I’m your virtual assistant from Hiring Partner.\n\nCan I know your **full name**?"

    elif stage == "full_name":
        info["Full Name"] = user_input
        st.session_state.stage = "email"
        return "📧 What’s your **email address**?"

    elif stage == "email":
        info["Email"] = user_input
        st.session_state.stage = "phone"
        return "📞 Could you share your **phone number**?"

    elif stage == "phone":
        info["Phone"] = user_input
        st.session_state.stage = "experience"
        return "🧑‍💻 How many **years of experience** do you have?"

    elif stage == "experience":
        info["Experience"] = user_input
        st.session_state.stage = "position"
        return "🎯 What **position(s)** are you applying for?"

    elif stage == "position":
        info["Position"] = user_input
        st.session_state.stage = "location"
        return "📍 Where are you **currently located**?"

    elif stage == "location":
        info["Location"] = user_input
        st.session_state.stage = "tech_stack"
        return "💻 Please list your **tech stack** (e.g., Python, React, MongoDB)..."

    elif stage == "tech_stack":
        info["Tech Stack"] = user_input
        st.session_state.stage = "questioning"
        tech_q = get_technical_questions(user_input)
        code_q = get_coding_questions(user_input)
        st.session_state.tech_questions = tech_q.split("\n")
        st.session_state.code_questions = code_q.split("\n")
        return f"🧪 Here are technical questions:\n\n{tech_q}\n\n💡 Coding questions:\n\n{code_q}"

    elif stage == "questioning":
        st.session_state.stage = "job_rec"
        recs = get_job_recommendations(info["Position"], info["Location"])
        st.session_state.job_recommendations = recs
        if recs and "No jobs" not in recs[0]:
            return "💼 Based on your profile, here are some job recommendations:\n\n" + "\n\n".join(recs)
        else:
            return "❗ No jobs found for your profile. You can still download the report for review."

    elif stage == "job_rec":
        st.session_state.stage = "done"
        return "✅ That’s all I need for now. Thank you for your time! You’ll hear from us soon. 🙏"

    else:
        return "❓ Hmm, I didn’t quite get that. Could you please rephrase?"

# Chat display
with st.container():
    for i, msg in enumerate(st.session_state.messages):
        message(msg["content"], is_user=msg["role"] == "user", key=str(i))

# Chat input
if not st.session_state.end_chat:
    user_prompt = st.chat_input("Type here to talk to Hiring Partner...")
    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        bot_response = chat_logic(user_prompt)
        time.sleep(0.2)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.rerun()
else:
    st.success("✅ Chat ended. Refresh to restart.")
    with st.expander("📄 Candidate Summary"):
        for k, v in st.session_state.candidate_info.items():
            st.markdown(f"**{k}:** {v}")

        st.markdown("### 🧪 Technical Questions")
        for q in st.session_state.tech_questions:
            st.markdown(f"- {q}")

        st.markdown("### 💡 Coding Questions")
        for q in st.session_state.code_questions:
            st.markdown(f"- {q}")

        st.markdown("### 💼 Job Recommendations")
        for job in st.session_state.job_recommendations:
            st.markdown(job)

        if st.button("📄 Export as PDF"):
            pdf_file = export_pdf(
                st.session_state.candidate_info,
                st.session_state.tech_questions or ["No technical questions generated."],
                st.session_state.code_questions or ["No coding questions generated."],
                st.session_state.job_recommendations or ["No job recommendations available."]
            )
            with open(pdf_file, "rb") as f:
                st.download_button(label="📥 Download PDF", data=f, file_name="HiringPartner_Candidate_Report.pdf")

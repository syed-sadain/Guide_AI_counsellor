import streamlit as st
from groq import Groq
import json
import os
from dotenv import load_dotenv
from gtts import gTTS
import tempfile
import io

load_dotenv()

st.set_page_config(page_title="AI Counsellor", page_icon="🧠", layout="wide")

# ======================= GROQ =======================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ======================= UNIVERSITIES =======================
UNIVERSITIES = [
    {"name": "MIT", "country": "USA", "annual_cost_usd": 60000, "acceptance": "Very Low", "risk": "High", "level": "Dream"},
    {"name": "Stanford University", "country": "USA", "annual_cost_usd": 62000, "acceptance": "Very Low", "risk": "High", "level": "Dream"},
    {"name": "University of Toronto", "country": "Canada", "annual_cost_usd": 42000, "acceptance": "Medium", "risk": "Medium", "level": "Target"},
    {"name": "University of British Columbia", "country": "Canada", "annual_cost_usd": 38000, "acceptance": "Medium", "risk": "Low", "level": "Target"},
    {"name": "Imperial College London", "country": "UK", "annual_cost_usd": 52000, "acceptance": "Low", "risk": "High", "level": "Dream"},
    {"name": "UCL", "country": "UK", "annual_cost_usd": 48000, "acceptance": "Medium", "risk": "Medium", "level": "Target"},
    {"name": "Technical University of Munich", "country": "Germany", "annual_cost_usd": 8000, "acceptance": "Medium", "risk": "Low", "level": "Safe"},
    {"name": "ETH Zurich", "country": "Switzerland", "annual_cost_usd": 25000, "acceptance": "Low", "risk": "Medium", "level": "Dream"},
    {"name": "University of Melbourne", "country": "Australia", "annual_cost_usd": 45000, "acceptance": "Medium", "risk": "Medium", "level": "Target"},
    {"name": "NUS", "country": "Singapore", "annual_cost_usd": 38000, "acceptance": "Low", "risk": "High", "level": "Dream"},
    {"name": "University of Sydney", "country": "Australia", "annual_cost_usd": 42000, "acceptance": "Medium", "risk": "Medium", "level": "Target"},
    {"name": "University of Manchester", "country": "UK", "annual_cost_usd": 42000, "acceptance": "Medium", "risk": "Low", "level": "Safe"},
    {"name": "University of Waterloo", "country": "Canada", "annual_cost_usd": 36000, "acceptance": "Medium", "risk": "Medium", "level": "Target"},
    {"name": "Georgia Tech", "country": "USA", "annual_cost_usd": 48000, "acceptance": "Medium", "risk": "Medium", "level": "Target"},
    {"name": "RWTH Aachen", "country": "Germany", "annual_cost_usd": 6000, "acceptance": "High", "risk": "Low", "level": "Safe"},
    {"name": "University of Oxford", "country": "UK", "annual_cost_usd": 55000, "acceptance": "Very Low", "risk": "High", "level": "Dream"},
    {"name": "UC Berkeley", "country": "USA", "annual_cost_usd": 58000, "acceptance": "Low", "risk": "High", "level": "Dream"},
    {"name": "Monash University", "country": "Australia", "annual_cost_usd": 38000, "acceptance": "High", "risk": "Low", "level": "Safe"},
]

# ======================= SESSION STATE =======================
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "email" not in st.session_state:
    st.session_state.email = None
if "current_stage" not in st.session_state:
    st.session_state.current_stage = 1
if "messages" not in st.session_state:
    st.session_state.messages = []
if "shortlisted" not in st.session_state:
    st.session_state.shortlisted = []
if "locked" not in st.session_state:
    st.session_state.locked = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}

stages = ["Login/Onboarding", "Dashboard", "AI Counsellor", "Shortlisting", "University Locking", "Application Guidance"]

# ======================= SIDEBAR =======================
with st.sidebar:
    st.title("🧠 AI Counsellor")
    st.markdown("**Study Abroad Journey**")
    if st.session_state.user_id:
        st.success(f"Logged in as {st.session_state.get('email', 'User')}")
        st.progress((st.session_state.current_stage - 1) / 5)
        st.write(f"**Stage {st.session_state.current_stage}/6**")
    if st.button("Reset All Progress"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ======================= MAIN UI =======================
st.title("AI Counsellor - Study Abroad Platform")

if st.session_state.current_stage == 1:
    st.subheader("Welcome - Login or Sign Up")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        if st.button("Login"):
            if email:
                st.session_state.user_id = 1
                st.session_state.email = email
                if st.session_state.user_profile:
                    st.session_state.current_stage = 2
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Please enter an email")

    with tab2:
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="signup_email")
        if st.button("Create Account & Start Onboarding"):
            if name and email:
                st.session_state.user_id = 1
                st.session_state.email = email
                st.success("Account created! Complete onboarding below.")
                st.rerun()

    if st.session_state.user_id and not st.session_state.user_profile:
        st.subheader("Mandatory Onboarding")
        with st.form("onboarding_form"):
            education_level = st.selectbox("Current Education Level", ["Bachelor's", "Master's", "PhD"])
            degree = st.text_input("Degree / Major")
            grad_year = st.number_input("Expected Graduation Year", 2025, 2035, 2026)
            gpa = st.number_input("GPA (optional)", 0.0, 10.0, 7.5, 0.1)
            target_degree = st.selectbox("Intended Degree", ["Bachelor's", "Master's", "MBA", "PhD"])
            field = st.text_input("Field of Study", "Computer Science")
            intake_year = st.number_input("Target Intake Year", 2026, 2030, 2026)
            countries = st.multiselect("Preferred Countries", ["USA", "Canada", "UK", "Germany", "Australia", "Singapore"], default=["Canada", "Germany"])
            budget = st.slider("Annual Budget (USD)", 5000, 80000, 35000, 1000)
            funding = st.selectbox("Funding Plan", ["Self-funded", "Scholarship", "Loan"])
            ielts = st.selectbox("IELTS/TOEFL Status", ["Not started", "In progress", "Completed"])
            gre = st.selectbox("GRE/GMAT Status", ["Not started", "In progress", "Completed"])
            sop = st.selectbox("SOP Status", ["Not started", "Draft", "Ready"])

            if st.form_submit_button("Complete Onboarding"):
                profile = {
                    "education_level": education_level,
                    "degree": degree,
                    "grad_year": int(grad_year),
                    "gpa": float(gpa),
                    "target_degree": target_degree,
                    "field": field,
                    "intake_year": int(intake_year),
                    "countries": countries,
                    "budget": int(budget),
                    "funding": funding,
                    "ielts": ielts,
                    "gre": gre,
                    "sop": sop
                }
                st.session_state.user_profile = profile
                st.session_state.current_stage = 2
                st.success("Onboarding completed successfully!")
                st.rerun()

elif st.session_state.current_stage == 2:
    st.subheader("Dashboard")
    profile = st.session_state.user_profile
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Profile Strength", "Strong" if profile.get("gpa", 0) >= 7.5 else "Average")
    with col2:
        st.metric("Budget", f"${profile.get('budget', 0):,}/year")
    with col3:
        st.metric("Locked Unis", len(st.session_state.locked))

    if st.button("Go to AI Counsellor", type="primary"):
        st.session_state.current_stage = 3
        st.rerun()

elif st.session_state.current_stage == 3:
    st.subheader("AI Counsellor")
    st.caption("Chat with Saanvi - Your empathetic AI study abroad counsellor")

    # Display chat history
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                if st.button("🔊 Hear this response", key=f"speak_{i}"):
                    try:
                        tts = gTTS(text=msg["content"], lang="en", slow=False)
                        audio_bytes = io.BytesIO()
                        tts.write_to_fp(audio_bytes)
                        audio_bytes.seek(0)
                        st.audio(audio_bytes, format="audio/mp3")
                    except Exception as e:
                        st.error(f"Could not generate audio: {e}")

    prompt = st.chat_input("Ask Saanvi anything about your study abroad journey...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Saanvi is thinking..."):
                if client and GROQ_API_KEY:
                    sys_prompt = f"""You are Saanvi, a warm, empathetic, and supportive AI study abroad counsellor. 
                    Speak naturally like a caring older sister - friendly, encouraging, and easy to understand.
                    Use simple language. Be practical, patient, and personalized.

                    User Profile: {json.dumps(st.session_state.user_profile)}
                    Shortlisted: {len(st.session_state.shortlisted)}
                    Locked: {len(st.session_state.locked)}
                    Current stage: {stages[st.session_state.current_stage-1]}"""

                    recent_messages = st.session_state.messages[-10:]
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": sys_prompt}] + recent_messages,
                        temperature=0.75,
                        max_tokens=800
                    )
                    reply = response.choices[0].message.content
                else:
                    reply = "I'm here to support you! How can I help with your study abroad plans today?"

                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

                # Auto speak latest response
                try:
                    tts = gTTS(text=reply, lang="en", slow=False)
                    audio_bytes = io.BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    st.audio(audio_bytes, format="audio/mp3")
                except Exception as e:
                    st.error(f"Could not play audio: {e}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("Discover Universities"):
            st.session_state.current_stage = 4
            st.rerun()

elif st.session_state.current_stage == 4:
    st.subheader("University Discovery")
    profile = st.session_state.user_profile
    budget = profile.get("budget", 40000)
    countries = profile.get("countries", [])
    filtered = [u for u in UNIVERSITIES if u["country"] in countries and u["annual_cost_usd"] <= budget * 1.2]

    for uni in filtered:
        with st.expander(f"⭐ {uni['name']} ({uni['country']}) - {uni['level']}"):
            st.write(f"**Cost**: ${uni['annual_cost_usd']:,}/year")
            st.write(f"**Acceptance**: {uni['acceptance']} | **Risk**: {uni['risk']}")
            if st.button("Shortlist", key=f"short_{uni['name']}"):
                if not any(s["name"] == uni["name"] for s in st.session_state.shortlisted):
                    st.session_state.shortlisted.append({
                        "name": uni["name"],
                        "country": uni["country"],
                        "annual_cost_usd": uni["annual_cost_usd"],
                        "acceptance": uni["acceptance"],
                        "risk": uni["risk"],
                        "level": uni["level"]
                    })
                    st.success(f"{uni['name']} shortlisted!")
                else:
                    st.info("Already shortlisted")
    if st.button("Go to Locking", type="primary"):
        st.session_state.current_stage = 5
        st.rerun()

elif st.session_state.current_stage == 5:
    st.subheader("Lock Universities")
    st.info("Lock at least 1 university to unlock application guidance.")
    for uni_dict in st.session_state.shortlisted:
        uni = {"name": uni_dict["name"], "country": uni_dict["country"], "annual_cost_usd": uni_dict["annual_cost_usd"]}
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{uni['name']}** - ${uni['annual_cost_usd']:,}")
        with col2:
            if uni["name"] not in [l.get("name") for l in st.session_state.locked]:
                if st.button("Lock", key=f"lock_{uni['name']}"):
                    st.session_state.locked.append(uni)
                    st.success("Locked!")
                    st.rerun()

    if len(st.session_state.locked) >= 1 and st.button("Proceed to Application Guidance", type="primary"):
        st.session_state.current_stage = 6
        st.rerun()

elif st.session_state.current_stage == 6:
    st.subheader("Application Guidance & To-Dos")
    if not st.session_state.tasks:
        st.session_state.tasks = [
            {"task": "Complete IELTS/TOEFL", "done": False},
            {"task": "Draft your Statement of Purpose (SOP)", "done": False},
            {"task": f"Gather documents for {st.session_state.locked[0]['name'] if st.session_state.locked else 'your university'}", "done": False},
            {"task": "Submit applications before deadline", "done": False}
        ]

    for i, task in enumerate(st.session_state.tasks):
        done = st.checkbox(task["task"], value=task["done"], key=f"task_{i}")
        if done != task["done"]:
            task["done"] = done
            st.rerun()

    if st.button("Finish Journey"):
        st.balloons()
        st.success("Congratulations! Your study abroad journey is on track.")

st.caption("AI Counsellor • Session-State Only • Natural Voice (gTTS)")
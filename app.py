import streamlit as st
import pandas as pd
import plotly.express as px

from firebase_config import auth
from pdf_utils import extract_text_from_pdf
from ai_engine import analyze_resume

from backend_db import (
    save_analysis,
    get_user_history,
    get_dashboard_stats
)

from gemini_engine import generate_ai_content
from pdf_generator import generate_pdf


# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="AI Resume Assistant",
    layout="wide"
)

st.title("AI Resume Assistant")
st.caption("Analyze resumes, compare with job descriptions, and generate career insights.")


# ==================================================
# SESSION STATE
# ==================================================
if "user" not in st.session_state:
    st.session_state.user = None

if "user_email" not in st.session_state:
    st.session_state.user_email = ""


# ==================================================
# LOGOUT FUNCTION
# ==================================================
def logout():
    st.session_state.user = None
    st.session_state.user_email = ""
    st.rerun()


# ==================================================
# DASHBOARD UI
# ==================================================
def dashboard():
    st.subheader("📊 Dashboard")

    stats = get_dashboard_stats(st.session_state.user_email)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Analyses", stats.get("total", 0))

    with col2:
        st.metric("Average ATS Score", stats.get("avg_score", 0))

    with col3:
        st.metric("Best ATS Score", stats.get("max_score", 0))

    history = get_user_history(st.session_state.user_email)

    if history:
        scores = [
            {"Analysis": i + 1, "ATS Score": item.get("ats_score", 0)}
            for i, item in enumerate(history)
        ]

        df = pd.DataFrame(scores)

        fig = px.line(df, x="Analysis", y="ATS Score", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No analyses available yet.")


# ==================================================
# RESUME ANALYSIS UI
# ==================================================
def resume_analysis():
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    job_description = st.text_area("Paste Job Description")

    if uploaded_file and job_description.strip():

        resume_text = extract_text_from_pdf(uploaded_file)

        st.subheader("Extracted Resume")
        st.text_area("Resume Text", resume_text, height=250)

        # ML/ATS analysis
        result = analyze_resume(resume_text, job_description)

        # Gemini AI
        try:
            with st.spinner("Generating AI insights..."):
                gemini_output = generate_ai_content(resume_text, job_description)
        except Exception as e:
            gemini_output = f"⚠️ Gemini AI temporarily unavailable.\n\nError: {str(e)}"

        # ======================
        # OUTPUT SECTION
        # ======================
        st.subheader("🤖 Gemini AI Insights")
        st.markdown(gemini_output)

        st.subheader("ATS Score")
        st.progress(int(result["score"]))
        st.write(f"{result['score']} / 100")

        st.subheader("Matched Skills")
        st.write(result["matched"])

        st.subheader("Missing Skills")
        st.write(result["missing"])

        st.subheader("Cover Letter")
        st.text_area("Cover Letter", result["cover_letter"], height=220)

        st.download_button(
            "Download Cover Letter",
            data=result["cover_letter"],
            file_name="cover_letter.txt"
        )

        st.subheader("Interview Questions")
        for q in result["interview_questions"]:
            st.write(f"• {q}")

        st.subheader("LinkedIn Summary")
        st.text_area("LinkedIn Summary", result["linkedin_summary"], height=180)

        # ======================
        # PDF REPORT
        # ======================
        pdf_path = "resume_report.pdf"

        generate_pdf(
            pdf_path,
            result["score"],
            result["matched"],
            result["missing"],
            result["cover_letter"],
            result["linkedin_summary"],
            gemini_output,
        )

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                "📄 Download AI Report (PDF)",
                data=pdf_file,
                file_name="AI_Resume_Report.pdf",
                mime="application/pdf",
            )

        # ======================
        # SAVE ANALYSIS
        # ======================
        if st.button("💾 Save Analysis"):

            save_analysis(
                user_email=st.session_state.user_email,
                resume_text=resume_text,
                job_description=job_description,
                ats_score=result["score"],
                matched_skills=result["matched"],
                missing_skills=result["missing"],
                cover_letter=result["cover_letter"],
                linkedin_summary=result["linkedin_summary"],
                ai_insights=gemini_output,
            )

            st.success("Analysis saved successfully!")

    st.button("🚪 Logout", on_click=logout)


# ==================================================
# HISTORY UI
# ==================================================
def analysis_history():
    st.subheader("📜 Your Previous Analyses")

    history = get_user_history(st.session_state.user_email)

    if history:
        for i, item in enumerate(history, start=1):

            with st.expander(f"📄 Analysis {i} | ATS Score: {item.get('ats_score', 0)}"):

                st.metric("ATS Score", f"{item.get('ats_score', 0)} / 100")

                st.markdown("### ✅ Matched Skills")
                st.write(", ".join(item.get("matched_skills", [])) or "No matched skills")

                st.markdown("### ❌ Missing Skills")
                st.write(", ".join(item.get("missing_skills", [])) or "No missing skills")

                if item.get("cover_letter"):
                    st.text_area("Cover Letter", item["cover_letter"], height=200)

                if item.get("linkedin_summary"):
                    st.text_area("LinkedIn Summary", item["linkedin_summary"], height=150)

                if item.get("ai_insights"):
                    st.markdown("### 🤖 AI Insights")
                    st.markdown(item["ai_insights"])

    else:
        st.info("No saved analyses found.")

    st.button("🚪 Logout", on_click=logout)


# ==================================================
# LOGIN / SIGNUP
# ==================================================
def login_signup():

    menu = st.sidebar.selectbox("Menu", ["Login", "Sign Up"])

    if menu == "Sign Up":
        st.subheader("Create Account")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Sign Up"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("Account created successfully!")
            except Exception as e:
                st.error(str(e))

    else:
        st.subheader("Welcome Back")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)

                st.session_state.user = user
                st.session_state.user_email = email

                st.success("Login successful!")
                st.rerun()

            except Exception:
                st.error("Invalid credentials")


# ==================================================
# MAIN APP ROUTER
# ==================================================
if st.session_state.user:

    st.success(f"Logged in as: {st.session_state.user_email}")

    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Resume Analysis", "Analysis History", "Pricing"]
    )

    if page == "Dashboard":
        dashboard()

    elif page == "Resume Analysis":
        resume_analysis()

    elif page == "Analysis History":
        analysis_history()

    elif page == "Pricing":
        st.subheader("💰 Pricing Plans")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("""
            ### Free
            ₹0/month

            ✓ 3 Analyses/day
            ✓ ATS Score
            ✓ Resume Match
            """)

        with col2:
            st.success("""
            ### Premium
            ₹199/month

            ✓ Unlimited Analyses
            ✓ AI Resume Improvement
            ✓ Interview Coach
            ✓ Premium Reports
            """)

            st.button("Upgrade to Premium")

        with col3:
            st.warning("""
            ### Recruiter
            ₹999/month

            ✓ Bulk Resume Screening
            ✓ Candidate Ranking
            ✓ Interview Questions
            """)

else:
    login_signup()

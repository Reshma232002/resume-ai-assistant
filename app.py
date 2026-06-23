import streamlit as st
import pandas as pd
import plotly.express as px

from firebase_config import auth
from pdf_utils import extract_text_from_pdf
from ai_engine import analyze_resume
from gemini_engine import generate_ai_content
from pdf_generator import generate_pdf
from user_plan import can_use_service
from backend_db import (
    increment_usage,
    save_analysis,
    get_user_history,
    get_dashboard_stats,
    reset_daily_usage_if_needed
)

from payment import create_order, verify_payment, upgrade_user
import streamlit.components.v1 as components


# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="AI Resume Assistant",
    layout="wide"
)

st.title("AI Resume Assistant")
st.caption("Analyze resumes, compare with job descriptions, and generate career insights")


# ==================================================
# SESSION STATE
# ==================================================
if "user" not in st.session_state:
    st.session_state.user = None

if "user_email" not in st.session_state:
    st.session_state.user_email = ""


# ==================================================
# LOGOUT
# ==================================================
def logout():
    st.session_state.user = None
    st.session_state.user_email = ""
    st.rerun()


# ==================================================
# DASHBOARD
# ==================================================
def dashboard():
    reset_daily_usage_if_needed(st.session_state.user_email)

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
        df = pd.DataFrame([
            {"Analysis": i + 1, "ATS Score": item.get("ats_score", 0)}
            for i, item in enumerate(history)
        ])

        fig = px.line(df, x="Analysis", y="ATS Score", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No analyses yet.")


# ==================================================
# RESUME ANALYSIS
# ==================================================
def resume_analysis():
    reset_daily_usage_if_needed(st.session_state.user_email)

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    job_description = st.text_area("Paste Job Description")

    if uploaded_file and job_description.strip():

        allowed, message = can_use_service(st.session_state.user_email)

        if not allowed:
            st.error(message)
            st.stop()

        with st.spinner("Extracting resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)

        st.subheader("Extracted Resume")
        st.text_area("Resume Text", resume_text, height=250)

        with st.spinner("Running ATS Analysis..."):
            result = analyze_resume(resume_text, job_description)

        try:
            with st.spinner("Generating AI insights..."):
                gemini_output = generate_ai_content(resume_text, job_description)
        except Exception as e:
            gemini_output = f"AI error: {str(e)}"

        st.subheader("Gemini AI Insights")
        st.markdown(gemini_output)

        st.subheader("ATS Score")
        st.progress(int(result["score"]))
        st.write(f"{result['score']} / 100")

        st.subheader("Matched Skills")
        st.write(result["matched"])

        st.subheader("Missing Skills")
        st.write(result["missing"])

        st.subheader("Cover Letter")
        st.text_area("Cover Letter", result["cover_letter"], height=200)

        st.download_button(
            "Download Cover Letter",
            data=result["cover_letter"],
            file_name="cover_letter.txt"
        )

        st.subheader("Interview Questions")
        for i, q in enumerate(result["interview_questions"]):
            st.write(f"{i+1}. {q}")

        st.subheader("LinkedIn Summary")
        st.text_area("LinkedIn Summary", result["linkedin_summary"], height=150)

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
                "Download AI Report (PDF)",
                data=pdf_file,
                file_name="AI_Resume_Report.pdf",
                mime="application/pdf",
            )

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

            increment_usage(st.session_state.user_email)
            st.success("Saved successfully!")

    st.button("Logout", on_click=logout)


# ==================================================
# HISTORY
# ==================================================
def analysis_history():

    st.subheader("Previous Analyses")

    history = get_user_history(st.session_state.user_email)

    if history:
        for i, item in enumerate(history, 1):

            with st.expander(f"Analysis {i} | ATS: {item.get('ats_score', 0)}"):

                st.metric("ATS Score", f"{item.get('ats_score', 0)} / 100")

                st.write("Matched:", item.get("matched_skills", []))
                st.write("Missing:", item.get("missing_skills", []))

                if item.get("cover_letter"):
                    st.text_area("Cover Letter", item["cover_letter"], key=f"cl_{i}")

                if item.get("linkedin_summary"):
                    st.text_area("LinkedIn", item["linkedin_summary"], key=f"li_{i}")

                if item.get("ai_insights"):
                    st.markdown(item["ai_insights"])

    else:
        st.info("No saved analyses.")


# ==================================================
# LOGIN / SIGNUP
# ==================================================
def login_signup():

    menu = st.sidebar.selectbox("Menu", ["Login", "Sign Up"])

    if menu == "Sign Up":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Sign Up"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("Account created!")
            except Exception as e:
                st.error(e)

    else:

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            try:
                user = auth.sign_in_with_email_and_password(
                    email.strip(),
                    password
                )

                st.session_state.user = user
                st.session_state.user_email = email

                st.rerun()

            except Exception as e:
                st.error(f"Login failed: {str(e)}")


# ==================================================
# MAIN ROUTER
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

        st.subheader("Pricing Plans")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("Free: 1 analysis/day")

        with col2:
            st.success("Premium ₹99/month")

            if st.button("Pay ₹99 Premium"):
                order = create_order(99)

                checkout_html = f"""
                <script src="https://checkout.razorpay.com/v1/checkout.js"></script>

                <script>
                var options = {{
                    "key": "{st.secrets["RAZORPAY_KEY_ID"]}",
                    "amount": "9900",
                    "currency": "INR",
                    "order_id": "{order['id']}",

                    "handler": function (response) {{
                        window.parent.postMessage({{
                            order_id: "{order['id']}",
                            payment_id: response.razorpay_payment_id,
                            signature: response.razorpay_signature
                        }}, "*");
                    }}
                }};

                var rzp = new Razorpay(options);
                rzp.open();
                </script>
                """

                components.html(checkout_html, height=300)

        with col3:
            st.warning("Recruiter ₹299/month")

            if st.button("Pay ₹299 Recruiter"):

                order = create_order(299)

                checkout_html = f"""
                <script src="https://checkout.razorpay.com/v1/checkout.js"></script>

                <script>
                var options = {{
                    "key": "{st.secrets["RAZORPAY_KEY_ID"]}",
                    "amount": "29900",
                    "currency": "INR",
                    "order_id": "{order['id']}",

                    "handler": function (response) {{
                        window.parent.postMessage({{
                            order_id: "{order['id']}",
                            payment_id: response.razorpay_payment_id,
                            signature: response.razorpay_signature
                        }}, "*");
                    }}
                }};

                var rzp = new Razorpay(options);
                rzp.open();
                </script>
                """

                components.html(checkout_html, height=300)

else:
    login_signup()

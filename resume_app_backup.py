

import streamlit as st
from pypdf import PdfReader
from google import genai


st.set_page_config(
    page_title="AI Resume Assistant",
    page_icon="📄",
    layout="wide"
)

with st.sidebar:
    st.title("📄 AI Resume Assistant")
    st.write("Upload your resume and use AI-powered features.")

    
# Gemini Client
client = genai.Client(
    api_key=st.secrets["GOOGLE_API_KEY"]
)

st.set_page_config(
    page_title="AI Resume Assistant",
    page_icon="📄"
)
st.title("📄 AI Resume Assistant")

job_role = st.text_input(
    "🎯 Target Job Role",
    placeholder="e.g. Data Analyst"
)
job_description = st.text_area(
    "📋 Paste Job Description",
    height=200,
    placeholder="Paste the job description here..."
)

uploaded_file = st.file_uploader(
    "Upload your Resume",
    type=["pdf"]
)

if uploaded_file:

    reader = PdfReader(uploaded_file)

    resume_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            resume_text += text

    st.subheader("Resume Preview")

    st.text_area(
        "Resume Content",
        resume_text,
        height=250
    )

if st.button("Analyze Resume"):

        prompt = f"""
You are an ATS expert.

Target Job Role:
{job_role}

Analyze this resume and provide:

1. ATS Score
2. Strengths
3. Weaknesses
4. Missing Skills
5. Suggestions for Improvement

Resume:

{resume_text}
"""

        with st.spinner("Analyzing Resume..."):

    
             response = client.models.generate_content(
              model="gemini-2.0-flash",
              contents=prompt
              )



        st.success("Analysis Complete!")

        st.markdown(response.text)

        st.download_button(
         label="📥 Download Output",
         data=response.text,
         file_name="ai_output.txt",
         mime="text/plain"
        )    

if st.button("✨ Improve Resume"):

    improve_prompt = f"""
    You are an expert resume writer.

    Rewrite the following resume to make it more ATS-friendly for the role:
    {job_role}

    Improve:
    - Professional Summary
    - Experience bullet points
    - Skills section
    - Overall wording and clarity

    Resume:
    {resume_text}
    """

    with st.spinner("Improving Resume..."):

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=improve_prompt
        )

    st.success("Resume Improved!")
    st.markdown(response.text)      

    st.download_button(
         label="📥 Download Output",
         data=response.text,
         file_name="ai_output.txt",
         mime="text/plain"
        )  


if st.button("🎤 Generate Interview Questions"):

    interview_prompt = f"""
    Based on the following resume and target job role: {job_role},

    Generate:
    1. 10 technical interview questions
    2. 5 HR interview questions
    3. Short sample answers

    Resume:

    {resume_text}
    """

    with st.spinner("Generating Interview Questions..."):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=interview_prompt
        )

    st.success("Interview Questions Generated!")
    st.markdown(response.text)

    st.download_button(
         label="📥 Download Output",
         data=response.text,
         file_name="ai_output.txt",
         mime="text/plain"
        )  

   

if st.button("📊 Match Resume with JD"):

    jd_prompt = f"""
    Compare the following resume with the job description.

    Provide:
    1. Match Score (0-100%)
    2. Matching Skills
    3. Missing Skills
    4. Missing Keywords
    5. Suggestions to improve the resume

    Target Role:
    {job_role}

    Job Description:
    {job_description}

    Resume:
    {resume_text}
    """

    with st.spinner("Comparing Resume with Job Description..."):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=jd_prompt
        )

    st.success("Comparison Complete!")
    st.markdown(response.text)

    st.download_button(
         label="📥 Download Output",
         data=response.text,
         file_name="ai_output.txt",
         mime="text/plain"
        )  


if st.button("📝 Generate Cover Letter"):

    cover_letter_prompt = f"""
    Write a professional cover letter for the following job role:

    Target Role:
    {job_role}

    Based on this resume:

    {resume_text}

    The cover letter should:
    - Be professional and concise
    - Highlight relevant skills and experience
    - Express enthusiasm for the role
    - End with a polite closing
    """

    with st.spinner("Generating Cover Letter..."):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=cover_letter_prompt
        )

    st.success("Cover Letter Generated!")
    st.markdown(response.text)

    st.download_button(
         label="📥 Download Output",
         data=response.text,
         file_name="ai_output.txt",
         mime="text/plain"
        )  

if st.button("🛠️ Extract Skills"):

    skills_prompt = f"""
    Extract all technical and soft skills from this resume.

    Group them into:
    1. Programming Languages
    2. Tools & Technologies
    3. Cloud Platforms
    4. Soft Skills
    5. Certifications

    Resume:

    {resume_text}
    """

    with st.spinner("Extracting Skills..."):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=skills_prompt
        )

    st.success("Skills Extracted!")
    st.markdown(response.text)

    st.download_button(
         label="📥 Download Output",
         data=response.text,
         file_name="ai_output.txt",
         mime="text/plain"
        )  


if st.button("💼 Generate LinkedIn Summary"):

    linkedin_prompt = f"""
    Create a professional LinkedIn summary based on this resume.

    Target Role:
    {job_role}

    Resume:
    {resume_text}
    """

    with st.spinner("Generating LinkedIn Summary..."):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=linkedin_prompt
        )

    st.success("LinkedIn Summary Generated!")
    st.markdown(response.text)

    st.download_button(
         label="📥 Download Output",
         data=response.text,
         file_name="ai_output.txt",
         mime="text/plain"
        )  


user_question = st.text_input(
    "💬 Ask a question about your resume"
)

if st.button("Ask AI"):

    chat_prompt = f"""
    Resume:
    {resume_text}

    User Question:
    {user_question}

    Answer based only on the resume content.
    """

    with st.spinner("Thinking..."):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=chat_prompt
        )

    st.markdown(response.text) 

    st.download_button(
         label="📥 Download Output",
         data=response.text,
         file_name="ai_output.txt",
         mime="text/plain"
        )  
    


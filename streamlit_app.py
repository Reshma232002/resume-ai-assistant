''' import streamlit as st
from google import genai

client = genai.Client(
    api_key=st.secrets["GOOGLE_API_KEY"]
)

st.title("My First AI App 🚀")

question = st.text_area("Ask anything")

if st.button("Ask AI"):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question
    )
    st.write(response.text) '''


'''import streamlit as st

st.set_page_config(
    page_title="AI Resume Assistant",
    page_icon="📄"
)

st.title("📄 AI Resume Assistant")

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf"]
)

if uploaded_file:
    st.success("Resume uploaded successfully!")'''

import streamlit as st
from pypdf import PdfReader

st.set_page_config(
    page_title="AI Resume Assistant",
    page_icon="📄"
)

st.title("📄 AI Resume Assistant")

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf"]
)

if uploaded_file:

    reader = PdfReader(uploaded_file)

    resume_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            resume_text += text

    st.subheader("Extracted Resume Text")

    st.text_area(
        "Resume Content",
        resume_text,
        height=300
    )
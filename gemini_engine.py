import google.generativeai as genai
import os

# ==================================================
# GEMINI CONFIGURATION
# ==================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None


# ==================================================
# GENERATE AI CONTENT
# ==================================================

def generate_ai_content(resume_text, job_description):

    # If API key is missing
    if model is None:
        return """
⚠️ Gemini API Key Not Found

Please set:

GEMINI_API_KEY

Environment variable before running the application.
"""

    prompt = f"""
You are an expert ATS Resume Analyzer.

Compare the resume and job description.

Provide:

1. ATS Score
2. Matched Skills
3. Missing Skills
4. Cover Letter
5. LinkedIn Summary
6. Interview Questions

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    try:

        response = model.generate_content(prompt)

        if hasattr(response, "text"):
            return response.text

        return "No AI response generated."

    except Exception as e:

        return f"""
⚠️ Gemini API Error

Reason:
{str(e)}

ATS analysis will still work normally.
"""
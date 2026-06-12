
import streamlit as st

from google import genai

client = genai.Client(
    api_key=st.secrets["GOOGLE_API_KEY"]
)

question = input("Ask Gemini anything: ")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=question
)

print("\nGemini says:\n")
print(response.text)
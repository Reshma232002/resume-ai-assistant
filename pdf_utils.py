import fitz  # PyMuPDF


def extract_text_from_pdf(uploaded_file):
    """Extract all text from a PDF uploaded through Streamlit."""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()

    return text
import streamlit as st
import fitz
import ollama
import requests

 
st.markdown("""
<style>
.main-title {
    font-size: 36px;
    font-weight: bold;
    color: #1f77b4;
}

.claim-box {
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #ddd;
    margin-bottom: 10px;
}

.verified {
    color: green;
    font-weight: bold;
}

.unverified {
    color: orange;
    font-weight: bold;
}

.false {
    color: red;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# PAGE SETTINGS
# -----------------------------------
st.set_page_config(
    page_title="Fact Check AI",
    page_icon="✅",
    layout="wide"
)

# -----------------------------------
# TITLE
# -----------------------------------
st.markdown("<div class='main-title'>✅ Fact Check AI Dashboard</div>", unsafe_allow_html=True)
st.subheader("Upload PDF → Extract Claims → Verify with Live Web Data")

# -----------------------------------
# FILE UPLOADER
# -----------------------------------
uploaded_file = st.file_uploader(
    "Upload PDF File",
    type=["pdf"]
)

# -----------------------------------
# PDF TEXT EXTRACTION
# -----------------------------------
def extract_text_from_pdf(pdf_file):
    text = ""

    pdf_document = fitz.open(
        stream=pdf_file.read(),
        filetype="pdf"
    )

    for page in pdf_document:
        text += page.get_text()

    return text

# -----------------------------------
# CLAIM EXTRACTION USING OLLAMA
# -----------------------------------
def extract_claims(text):

    prompt = f"""
You are a strict information extraction system.

CRITICAL RULES:
- Extract ONLY sentences that exist EXACTLY in the text
- DO NOT add, rewrite, summarize, or explain anything
- DO NOT create stories or examples
- If information is not explicitly present, ignore it completely
- Output ONLY bullet points

TEXT:
{text}

OUTPUT:
"""

    response = ollama.chat(
        model='llama3.2',
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )

    return response['message']['content']

# -----------------------------------
# CLAIM VERIFICATION FUNCTION
# -----------------------------------
from serpapi import GoogleSearch

SERPAPI_KEY = "9356321447da23a80a35b09c06f5d99a77fb0b59fd0af1ee361eb00096104ef4"

def verify_claim(claim):

    try:
        params = {
            "engine": "google",
            "q": claim,
            "api_key": SERPAPI_KEY
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        snippets = []

        if "organic_results" in results:

            for r in results["organic_results"][:3]:
                if "snippet" in r:
                    snippets.append(r["snippet"])

        score = len(snippets)

        if score >= 3:
            return "Likely Verified", "\n".join(snippets)

        elif score == 2:
            return "Possibly Verified", "\n".join(snippets)

        elif score == 1:
            return "Uncertain", "\n".join(snippets)

        else:
            return "False / No Evidence", "No reliable sources found"

    except Exception as e:
        return "API Error / Retry", str(e)
# -----------------------------------
# MAIN APP
# -----------------------------------
if uploaded_file is not None:

    st.success("PDF Uploaded Successfully!")

    extracted_text = extract_text_from_pdf(uploaded_file)

    st.subheader("📄 Extracted Text")

    st.text_area(
        "PDF Content",
        extracted_text,
        height=250
    )

    # ✅ BUTTON BLOCK START
if st.button("🔍 Extract & Verify Claims"):

    with st.spinner("Analyzing and verifying claims..."):

        claims = extract_claims(extracted_text)

    st.subheader("📌 Claims Verification Report")

    # -------------------------------
    # DASHBOARD COUNTERS
    # -------------------------------
    verified = 0
    uncertain = 0
    false = 0
    total = 0

    # -------------------------------
    # PROCESS EACH CLAIM (INSIDE BUTTON)
    # -------------------------------
    for claim in claims.split("\n"):

        claim = claim.strip()

        if claim:

            status, evidence = verify_claim(claim)

            total += 1

            if "Likely Verified" in status:
                verified += 1
            elif "Possibly" in status:
                uncertain += 1
            else:
                false += 1

            # -------------------------------
            # EXPANDABLE CLAIM UI
            # -------------------------------
            with st.expander("📌 Claim Details"):

                st.markdown(f"""
                <div style="border:1px solid #ddd;
                            padding:12px;
                            border-radius:10px;
                            background-color:#f9f9f9;
                            font-size:15px;">
                <b>📌 Claim:</b> {claim}
                </div>
                """, unsafe_allow_html=True)

                if "Likely Verified" in status:
                    st.success(f"Status: {status}")
                elif "Possibly" in status:
                    st.warning(f"Status: {status}")
                else:
                    st.error(f"Status: {status}")

                st.info(f"Evidence: {evidence}")

    # -------------------------------
    # SUMMARY DASHBOARD
    # -------------------------------
    st.markdown("## 📊 Document Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Claims", total)
    col2.metric("Verified", verified)
    col3.metric("Uncertain", uncertain)
    col4.metric("False", false)
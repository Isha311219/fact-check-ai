import streamlit as st
import fitz
import requests
from serpapi import GoogleSearch

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Fact Check AI",
    page_icon="✅",
    layout="wide"
)

# -----------------------------------
# UI STYLE
# -----------------------------------
st.markdown("""
<style>
.main-title {
    font-size: 36px;
    font-weight: bold;
    color: #1f77b4;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>✅ Fact Check AI Dashboard</div>", unsafe_allow_html=True)
st.subheader("Upload PDF → Extract Claims → Verify with Live Web Data")

# -----------------------------------
# FILE UPLOAD
# -----------------------------------
uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])

# -----------------------------------
# PDF TEXT EXTRACTION
# -----------------------------------
def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")

    for page in pdf_document:
        text += page.get_text()

    return text

# -----------------------------------
# CLAIM EXTRACTION 
# -----------------------------------
def extract_claims(text):

    sentences = text.split(".")
    claims = []

    keywords = [
        "million", "billion", "percent", "year",
        "India", "OpenAI", "founded", "report", "data"
    ]

    for s in sentences:
        s = s.strip()

        if len(s) > 20 and any(k.lower() in s.lower() for k in keywords):
            claims.append("• " + s)

    return "\n".join(claims)

# -----------------------------------
# SERPAPI KEY 
# -----------------------------------
SERPAPI_KEY = ""

# -----------------------------------
# CLAIM VERIFICATION FUNCTION
# -----------------------------------
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

    st.text_area("PDF Content", extracted_text, height=250)

    # -----------------------------------
    # BUTTON ACTION
    # -----------------------------------
    if st.button("🔍 Extract & Verify Claims"):

        with st.spinner("Analyzing and verifying claims..."):

            claims = extract_claims(extracted_text)

        st.subheader("📌 Claims Verification Report")

        # COUNTERS
        verified = 0
        uncertain = 0
        false = 0
        total = 0

        # PROCESS CLAIMS
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

                with st.expander("📌 Claim Details"):

                    st.markdown(f"### {claim}")

                    if "Likely Verified" in status:
                        st.success(f"Status: {status}")
                    elif "Possibly" in status:
                        st.warning(f"Status: {status}")
                    else:
                        st.error(f"Status: {status}")

                    st.info(f"Evidence: {evidence}")

        # SUMMARY DASHBOARD
        st.markdown("## 📊 Document Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Claims", total)
        col2.metric("Verified", verified)
        col3.metric("Uncertain", uncertain)
        col4.metric("False", false)

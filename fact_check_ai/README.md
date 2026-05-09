# Fact Check AI
## 🚀 Overview

Fact Check AI is an AI-powered web application that automatically extracts factual claims from PDF documents and verifies them using live web data.

It acts as a **"Truth Layer"** that detects misinformation, outdated statistics, and hallucinated claims in content and classifies them as:

- ✅ Verified  
- ⚠️ Inaccurate  
- ❌ False  

This project is designed for real-world use cases like:
- Marketing content validation  
- Research fact-checking  
- AI-generated content verification  

---

## 🎯 Key Features

### 📄 1. PDF Processing
- Upload any PDF document
- Extract raw text using PyMuPDF

### 🧠 2. AI-Based Claim Extraction
- Uses Ollama (LLM: llama3.2)
- Extracts only factual claims (stats, dates, numbers, statements)

### 🌐 3. Live Web Verification
- Uses SerpAPI Google Search API
- Cross-checks claims with real-time web data

### 📊 4. Smart Classification Engine
Each claim is classified as:
- **Verified** → Strong supporting evidence found
- **Inaccurate** → Weak or partial evidence
- **False** → No evidence found


## 🏗️ Tech Stack

- Python 🐍
- Streamlit 🎈
- PyMuPDF (fitz)
- Ollama (LLM)
- SerpAPI (Google Search API)
- Requests

 ## Run Locally
pip install -r requirements.txt
streamlit run app.py


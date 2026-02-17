# 🩸 HemoSense  
### AI-Powered Blood Report Analysis Platform

HemoSense is an intelligent health insights agent that analyzes blood reports and generates structured, personalized medical summaries using a multi-model AI architecture.

Built for reliability, scalability, and real-world deployment.

---

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" />
  <img src="https://img.shields.io/badge/Framework-Streamlit-red" />
  <img src="https://img.shields.io/badge/Database-Supabase-green" />
  <img src="https://img.shields.io/badge/AI-Groq-purple" />
  <img src="https://img.shields.io/badge/License-MIT-blue" />
</p>

---

## 🚀 Overview

HemoSense enables users to upload blood test reports in PDF format and receive:

- Structured parameter extraction
- AI-generated health insights
- Risk identification
- Context-aware medical explanations
- Personalized recommendations

The system uses a cascading multi-model architecture to ensure high availability and response reliability.

---

## 🧠 Architecture

HemoSense implements a **multi-layer AI fallback system**:

1. Primary LLM processes report data
2. Secondary model activates on failure
3. Tertiary model ensures redundancy
4. Structured validation before UI rendering

This guarantees robustness under model failure or rate limits.

---

## 🌟 Core Features

- 📄 Blood report PDF upload (up to 20MB)
- 🔍 Intelligent parameter extraction
- 🧠 AI-generated medical interpretation
- 🔄 Multi-model fallback handling
- 🔐 Secure user authentication (Supabase Auth)
- 🗂️ Session history & report tracking
- ⚡ Real-time interactive UI
- 🛡️ Input validation & secure secret management

---

## 🛠 Tech Stack

### Frontend
- Streamlit

### Backend & Database
- Supabase
- Supabase Authentication

### AI Infrastructure
- Groq API
  - meta-llama/llama-4-maverick-17b-128e-instruct
  - llama-3.3-70b-versatile
  - llama-3.1-8b-instant
  - llama3-70b-8192

### PDF Processing
- PDFPlumber
- python-magic / python-magic-bin

---

## 🤝 Collaborators

| Profile | Name | GitHub |
|--------|------|--------|
| <img src="https://github.com/LazyCoderror101.png" width="60" height="60" style="border-radius:50%;"> | LazyCoder | [@LazyCoder](https://github.com/LazyCoderror101) |
| <img src="https://github.com/nirmalyamohanty.png" width="60" height="60" style="border-radius:50%;"> | Nirmalya K. Mohanty | [@NirmalyaMohanty](https://github.com/nirmalyamohanty) |

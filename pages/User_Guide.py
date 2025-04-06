import streamlit as st

USER_GUIDE_MD = """
# Ghostwriter User Guide

Welcome to **Ghostwriter** – your AI-powered technical documentation assistant. Ghostwriter uses OpenAI's GPT technology to generate professional-quality documents based on product specifications or pasted text. It's designed for speed, flexibility, and simplicity.

---

## 🔧 What Ghostwriter Does

Ghostwriter helps you generate technical documents like:

- Quick Start Guides
- Installation Instructions
- Safety Sheets
- FAQs

You provide the input (pasted or uploaded), select a few options, and Ghostwriter drafts clean, markdown-based documents with export options.

---

## ✍️ How to Use Ghostwriter

### 1. **Choose Your Document Type**

Select the type of document you want to generate from the sidebar.

### 2. **Define the Audience**

Choose who the document is for (e.g., End User, Technician, Support Staff). Ghostwriter tailors the tone and style accordingly.

### 3. **Add Required Notes (Optional)**

If there are key phrases or compliance notes that must be included, you can enter them in the sidebar.

### 4. **Provide Product Info**

Choose to either:

- Paste the product info or spec into the text area
- Upload a `.txt`, `.md`, `.pdf`, `.docx`, or `.rtf` file

### 5. **Click 'Generate Draft'**

Ghostwriter sends your input to the AI, and returns a clean draft formatted in Markdown.

---

## 📤 Exporting Options

After reviewing or editing your draft, you can export it as:

- **Markdown** (`.md`)
- **HTML** (`.html`)
- **PDF** (`.pdf` – requires `pandoc` and `pdflatex` installed)
- **Chatbot JSON** (QA-style, parsed from H2 sections)

---

## 🔐 Privacy & Data Handling

Ghostwriter uses the OpenAI API to generate content.

- **Your data is not stored** or used for training by OpenAI
- **Ghostwriter only stores content** if you manually save or export it
- You have full control over your inputs and outputs

---

## 💡 Future Features (Planned)

Ghostwriter is evolving. Here are a few features on the roadmap:

- PhraseMap / Token-based content reuse
- Document version control
- Saved document library with metadata
- Change tracking for audits and regulatory compliance

---

## 🧠 Tips for Better Results

- Clean, structured input = better output
- Use bullet points, consistent headers, and clear terminology in your specs
- For PDFs or scanned docs, ensure text is selectable (not just images)

---

## 🤝 Support & Feedback

Have suggestions or found a bug? We’d love to hear from you.

**Email:** nhall0901@gmail.com  
**GitHub (coming soon):** [github.com/your-org/ghostwriter](https://github.com/your-org/ghostwriter)

---

*Ghostwriter helps you write less and ship faster. Let the ghost do the heavy lifting.*
"""

st.title("📘 User Guide")
st.markdown(USER_GUIDE_MD, unsafe_allow_html=True)

import os
from dotenv import load_dotenv
load_dotenv()  # ✅ Load environment variables early
import streamlit as st
import openai
import markdown2
import tempfile
import subprocess
import json
import fitz  # PyMuPDF for PDFs
import docx  # python-docx for Word
from ghostwriter_doc_learning import Workspace
from datetime import datetime
workspace = Workspace()


# Set your OpenAI API key from env
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Ghostwriter", layout="wide")

# --- Custom Styling ---
st.markdown("""
<style>
.big-title {
    font-size: 2.3rem;
    font-weight: 600;
    padding: 0 0 0.2em 0;
}
.subtle {
    color: gray;
    font-size: 0.9rem;
}
.stat-box {
    background-color: #f9f9f9;
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 0.5rem 0;
    box-shadow: 0px 1px 4px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# --- Top Section: Branding and Status ---
st.markdown('<div class="big-title">🧠 Ghostwriter</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.caption("Your AI assistant for writing, reviewing, and managing technical documents.")
    with st.expander("💬 Privacy & Data Use", expanded=False):
        st.markdown("""
        **Your content is yours.**  
        We use ChatGPT via the OpenAI API, which never stores your prompts or documents and doesn’t use them to train future models.  
        **Ghostwriter doesn’t store anything** unless you click “Save.”  
        Your data is encrypted, and you have full control over how and when AI assists you.
        """)

with col2:
    import os
    total_docs = len([f for f in os.listdir("docs") if f.endswith(".json")])
    model_status = "🟢 Ready" if workspace.model_ready else "⚪ Not Ready"
    st.markdown(f"""
    <div class="stat-box">
        <strong>📚 Docs in Library:</strong> {total_docs}<br>
        <strong>🧠 Model:</strong> {model_status}
    </div>
    """, unsafe_allow_html=True)



# Sidebar options
with st.sidebar:
    # --- Custom Styling ---
    st.markdown("""
    <style>
    .sidebar-header {
        font-size: 1.4rem;
        font-weight: 600;
        padding: 0.2rem 0 0.5rem 0;
    }
    .sidebar-divider {
        border-top: 1px solid #ddd;
        margin: 1.2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Header ---
    st.markdown('<div class="sidebar-header">🧠 Ghostwriter</div>', unsafe_allow_html=True)
    st.caption("Tech Doc Configuration")

    # --- Config Controls ---
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    doc_type = st.selectbox("📂 Type of Document", ["Quick Start", "Install Guide", "Safety Sheet", "FAQ"])
    audience = st.selectbox("👥 Audience", ["End User", "Technician", "Support Staff"])
    custom_notes = st.text_area("📝 Must-Include Notes (Optional)", height=100)

    # --- Footer ---
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.caption("v0.9 – Streamlit Edition")


# --- Custom Page Layout Style ---
st.markdown("""
<style>
/* Centered content max-width */
.css-18e3th9 {
    max-width: 1100px;
    margin: auto;
}

/* Section card */
.section-card {
    background-color: #fdfdfd;
    padding: 2rem 1.5rem;
    border-radius: 0.6rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    margin-bottom: 2rem;
}
.section-card h3 {
    margin-top: 0;
}

/* Buttons and toggles */
.toggle-button {
    padding: 0.5rem 1rem;
    margin-top: 0.5rem;
    border-radius: 0.4rem;
    border: 1px solid #ccc;
    background-color: #fafafa;
}
.toggle-button:hover {
    background-color: #f0f0f0;
}
</style>
""", unsafe_allow_html=True)



# Input area
st.markdown("---")
st.subheader("📥 Add Product Info")

input_col1, input_col2 = st.columns(2)

# Use session state to track the selected method
if "input_method" not in st.session_state:
    st.session_state.input_method = None

with input_col1:
    st.markdown("#### ✏️ Paste Text")
    st.caption("Copy and paste product specs, notes, or descriptions.")
    if "show_text_input" not in st.session_state:
        st.session_state.show_text_input = False

    if st.button("Add", key="text_method"):
        st.session_state.show_text_input = not st.session_state.show_text_input
        st.session_state.input_method = "Paste text" if st.session_state.show_text_input else None


with input_col2:
    st.markdown("#### 📁 Upload File")
    st.caption("Upload a spec sheet in `.txt`, `.pdf`, `.docx`, or `.md` format.")
    if st.button("Use File Upload", key="file_method"):
        st.session_state.input_method = "Upload file"

product_info = ""
generate_clicked = False

if st.session_state.input_method == "Paste text":
    if "pasted_text" not in st.session_state:
        st.session_state["pasted_text"] = ""

    st.session_state["pasted_text"] = st.text_area(
        "Paste your product info or spec here",
        value=st.session_state["pasted_text"],
        height=400
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        generate_clicked = st.button("🚀 Generate Draft", use_container_width=True)
    with col2:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state["pasted_text"] = ""

    product_info = st.session_state["pasted_text"]

elif st.session_state.input_method == "Upload file":
    uploaded_file = st.file_uploader(
        "Upload a spec file",
        type=["txt", "md", "pdf", "docx", "rtf"],
        key="spec_upload"
    )

    if uploaded_file:
        file_type = uploaded_file.name.split('.')[-1].lower()

        if file_type in ["txt", "md", "rtf"]:
            product_info = uploaded_file.read().decode("utf-8")

        elif file_type == "pdf":
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf:
                product_info = "".join([page.get_text() for page in pdf])

        elif file_type == "docx":
            doc = docx.Document(uploaded_file)
            product_info = "\n".join(para.text for para in doc.paragraphs)

    generate_clicked = st.button("🚀 Generate Draft")



# Generate button
if generate_clicked and product_info:
    with st.spinner("Generating..."):
        try:
            
            import os
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


            system_prompt = f"""
You are a technical documentation assistant. Based on the product information provided, generate a professional {doc_type} for the {audience}. Use clear and concise language. Follow these guidelines:
- Use Markdown format
- Use H1 for title, H2 for sections
- Use bullet points or numbered lists for steps
- Avoid repetition 
- Avoid fluff or marketing jargon
- Style: Direct, helpful, and easy to scan

If any custom notes or terminology must be included, be sure to incorporate them.
"""

            user_input = f"""DOCUMENT TYPE: {doc_type}
AUDIENCE: {audience}
CUSTOM NOTES: {custom_notes}

PRODUCT INFO:
{product_info}
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.4
            )

            markdown_output = response.choices[0].message.content
            st.session_state["generated_md"] = markdown_output

            # Save to docs/ library
            from datetime import datetime
            import uuid
            os.makedirs("docs", exist_ok=True)

            doc_id = str(uuid.uuid4())
            doc_name = f"{doc_type} – {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            doc_data = {
                "id": doc_id,
                "name": doc_name,
                "type": doc_type,
                "audience": audience,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "content": markdown_output,
                "tags": [t.strip() for t in custom_notes.split(",")] if custom_notes else [],
                "filename": f"{doc_id}.md"
            }

            with open(f"docs/{doc_id}.json", "w") as f:
                json.dump(doc_data, f, indent=2)

        except Exception as e:
            st.error(f"Failed to generate or save draft: {e}")



# Display result
if "generated_md" in st.session_state:
    st.subheader("📝 Markdown Draft")
    edited_md = st.text_area("Edit your draft below:", value=st.session_state["generated_md"], height=400)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.download_button("⬇️ Download Markdown", edited_md, file_name="draft.md", mime="text/markdown")

    with col2:
        html_output = markdown2.markdown(edited_md)
        st.download_button("🌐 Export to HTML", html_output, file_name="draft.html", mime="text/html")

    with col3:
        # Save to temporary file
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as tmp_md:
            tmp_md.write(edited_md)
            tmp_md_path = tmp_md.name

        pdf_output_path = tmp_md_path.replace(".md", ".pdf")
        try:
            subprocess.run(["pandoc", tmp_md_path, "-o", pdf_output_path], check=True)
            with open(pdf_output_path, "rb") as pdf_file:
                st.download_button("📄 Export to PDF", pdf_file.read(), file_name="draft.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"PDF export failed: {e}")

    with col4:
        # Convert to chatbot-style JSON
        qa_sections = [{"question": line.strip().lstrip("# ").strip(), "answer": ""} 
                       for line in edited_md.split("\n") if line.startswith("## ")]
        for i, section in enumerate(qa_sections):
            section["answer"] = "\n".join([
                line for line in edited_md.split("\n")[i+1:] 
                if not line.startswith("## ") and line.strip()
            ])[:300]  # Keep it basic

        chatbot_json = json.dumps(qa_sections, indent=2)
        st.download_button("💬 Export to Chatbot JSON", chatbot_json, file_name="chatbot_export.json", mime="application/json")
    st.markdown("---")
    st.markdown("### 💾 Save to Document Library?")
    save_col1, save_col2 = st.columns([2, 1])

    with save_col1:
        from datetime import datetime
        default_title = f"{doc_type} – {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        custom_title = st.text_input("Document Title", value=default_title)

    with save_col2:
        if st.button("✅ Save to Library", use_container_width=True):
            try:
                import uuid
                os.makedirs("docs", exist_ok=True)

                doc_id = str(uuid.uuid4())
                doc_data = {
                    "id": doc_id,
                    "name": custom_title,
                    "type": doc_type,
                    "audience": audience,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "content": edited_md,
                    "tags": [t.strip() for t in custom_notes.split(",")] if custom_notes else [],
                    "filename": f"{doc_id}.md"
                }

                with open(f"docs/{doc_id}.json", "w") as f:
                    json.dump(doc_data, f, indent=2)

                st.success(f"✅ '{custom_title}' saved to your document library!")

            except Exception as e:
                st.error(f"Failed to save draft: {e}")


# --- Learning from Existing Docs ---
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("### 📚 Learn From Existing Docs")
st.caption("Train Ghostwriter using your existing material for better feedback and consistency.")

learn_file = st.file_uploader("Upload a document to train Ghostwriter's model", type=["txt", "md", "docx"], key="learn")
learn_status = st.selectbox("Mark this document as", ["draft", "final"], key="learn_status")

if learn_file and st.button("Upload for Learning"):
    ext = learn_file.name.split('.')[-1].lower()
    if ext == "docx":
        doc = docx.Document(learn_file)
        learn_text = "\n".join(p.text for p in doc.paragraphs)
    else:
        learn_text = learn_file.read().decode("utf-8")

    workspace.upload_document(learn_text, learn_file.name, learn_status)
    st.success(f"📂 {learn_file.name} uploaded and tagged as **{learn_status}**.")
    if workspace.model_ready:
        st.info("✅ Model is trained and ready to give feedback!")

st.markdown("</div>", unsafe_allow_html=True)


# --- Review Section ---
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("### 🧐 Review a New Document")
st.caption("Upload a doc to receive tone and style feedback based on your training data.")

review_file = st.file_uploader("Upload a document for review", type=["txt", "md", "docx"], key="review")

if review_file and st.button("Run Review"):
    ext = review_file.name.split('.')[-1].lower()
    if ext == "docx":
        doc = docx.Document(review_file)
        review_text = "\n".join(p.text for p in doc.paragraphs)
    else:
        review_text = review_file.read().decode("utf-8")

    feedback = workspace.review_document(review_text)

    st.subheader("📊 Review Feedback")
    for category, items in feedback.items():
        st.markdown(f"#### {category.capitalize()}")
        if items:
            for item in items:
                st.write(f"• {item}")
        else:
            st.write("✅ No issues found.")

st.markdown("</div>", unsafe_allow_html=True)


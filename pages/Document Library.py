import streamlit as st
import os
import json
from datetime import datetime

st.set_page_config(page_title="📚 Document Library", layout="wide")
st.title("📚 Document Library")

DOCS_DIR = "docs"

# Load all JSON files from docs/
doc_files = [
    f for f in os.listdir(DOCS_DIR)
    if f.endswith(".json") and os.path.getsize(os.path.join(DOCS_DIR, f)) > 100
]

# Load and parse all valid documents
documents = []

for filename in doc_files:
    try:
        with open(os.path.join(DOCS_DIR, filename), "r") as f:
            doc = json.load(f)
            doc["__filename__"] = filename  # stash filename for deletion later
            documents.append(doc)
    except Exception as e:
        st.warning(f"⚠️ Skipping '{filename}': file is invalid or corrupt. ({e})")

# Sort by date/time descending
documents.sort(key=lambda d: d.get("date", ""), reverse=True)

# Display
for doc in documents:
    with st.expander(f"📄 {doc['name']} ({doc['type']}) – {doc['date']}"):
        st.markdown(f"**Audience:** {doc['audience']}")
        st.markdown(f"**Tags:** {', '.join(doc.get('tags', []))}")
        st.code(doc['content'], language="markdown")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("⬇️ Download Markdown", doc['content'], file_name=doc['filename'], mime="text/markdown")
        with col2:
            confirm_key = f"confirm_{doc['__filename__']}"
            delete_key = f"delete_{doc['__filename__']}"

            if st.checkbox(f"⚠️ Yes, I want to delete this document", key=confirm_key):
                if st.button(f"🗑️ Delete '{doc['name']}'", key=delete_key):
                    os.remove(os.path.join(DOCS_DIR, doc['__filename__']))
                    st.success(f"✅ '{doc['name']}' deleted.")
                    st.rerun()

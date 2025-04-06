import streamlit as st
import os
import json
from datetime import datetime

st.set_page_config(page_title="📚 Document Library", layout="wide")
st.title("📚 Document Library")

DOCS_DIR = "docs"

# Load all JSON files from docs/
doc_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".json")]

if not doc_files:
    st.info("No documents saved yet.")
else:
    for filename in sorted(doc_files, reverse=True):
        with open(os.path.join(DOCS_DIR, filename), "r") as f:
            doc = json.load(f)

        with st.expander(f"📄 {doc['name']} ({doc['type']}) – {doc['date']}"):
            st.markdown(f"**Audience:** {doc['audience']}")
            st.markdown(f"**Tags:** {', '.join(doc.get('tags', []))}")
            st.code(doc['content'], language="markdown")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("⬇️ Download Markdown", doc['content'], file_name=doc['filename'], mime="text/markdown")
            with col2:
                if st.button(f"🗑️ Delete '{doc['name']}'", key=filename):
                    os.remove(os.path.join(DOCS_DIR, filename))
                    st.experimental_rerun()

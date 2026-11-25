from pathlib import Path

import streamlit as st

DOCS = Path(__file__).resolve().parents[1] / "docs"
text = (DOCS / "guide_methodologique.md").read_text(encoding="utf-8")
pdf = DOCS / "guide_methodologique.pdf"

c1, c2, _ = st.columns([1, 1, 2])
if pdf.exists():
    c1.download_button("Télécharger le guide (PDF)", pdf.read_bytes(), "guide_methodologique.pdf",
                       "application/pdf", type="primary", icon=":material/picture_as_pdf:")
c2.download_button("Télécharger (Markdown)", text, "guide_methodologique.md", icon=":material/description:")
st.markdown(text)

import streamlit as st
import base64

st.title("Quant")

def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")

    st.markdown(
        f"""
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            width="100%"
            height="900"
            type="application/pdf">
        </iframe>
        """,
        unsafe_allow_html=True
    )

with st.expander("📄 Quant Reference PDF", expanded=True):
    display_pdf("GREMathFormulas.pdf")

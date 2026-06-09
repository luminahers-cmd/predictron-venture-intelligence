import streamlit as st
from google import genai

st.set_page_config(
    page_title="Predictron Venture Intelligence",
    page_icon="🚀",
    layout="wide"
)

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

st.title("🚀 Predictron Venture Intelligence")
st.subheader("AI-powered venture intelligence for founders, VCs, and hedge funds")

startup_name = st.text_input("Startup Name")

website = st.text_input("Website URL")

description = st.text_area(
    "Describe your startup",
    height=200
)

analyze = st.button("Analyze Startup")

if analyze:

    with st.spinner("Analyzing startup..."):

        prompt = f"""
You are a top venture capitalist.

Startup Name:
{startup_name}

Website:
{website}

Startup Description:
{description}

Provide:

1. One-sentence summary
2. Market opportunity
3. Competitive advantages
4. Key risks
5. Venture-scale potential (1-10)
6. Suggested investors
7. Investment memo

Be direct and analytical.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

    st.markdown(response.text)

    st.download_button(
        label="📄 Download Investment Memo",
        data=response.text,
        file_name=f"{startup_name}_investment_memo.txt",
        mime="text/plain"
    )
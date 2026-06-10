import logging

import streamlit as st

from config import get_api_key_status
from services.gemini_service import (
    GeminiAuthError,
    GeminiConfigurationError,
    GeminiResponseError,
    GeminiService,
    GeminiServiceError,
)
from utils.export import generate_simple_pdf
from utils.validators import validate_startup_inputs

logging.basicConfig(level=logging.INFO)
SUBHEADER_TEXT = (
    "AI-powered venture intelligence for founders, venture capitalists, family "
    "offices, and hedge funds"
)

st.set_page_config(
    page_title="Predictron Venture Intelligence",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 Predictron Venture Intelligence")
st.subheader(SUBHEADER_TEXT)

key_status = get_api_key_status(st.secrets)
service = None

with st.sidebar:
    st.markdown("### Gemini Configuration")
    st.caption(f"Key source: {key_status['source']}")

if not key_status["is_configured"]:
    st.error(key_status["message"])
    st.info(
        "Add GEMINI_API_KEY in Streamlit secrets or GOOGLE_API_KEY in environment "
        "variables, then reload the app."
    )
elif not key_status["is_valid"]:
    st.error(key_status["message"])
    st.warning("Use a Google AI Studio Gemini API key that starts with 'AIza'.")
else:
    try:
        service = GeminiService(api_key=key_status["api_key"])
    except GeminiConfigurationError as exc:
        st.error(str(exc))

startup_name = st.text_input("Startup Name")
website = st.text_input("Website URL")
description = st.text_area("Describe your startup", height=220)

analyze = st.button("Analyze Startup", disabled=service is None)

if analyze and service is not None:
    validation_errors = validate_startup_inputs(startup_name, website, description)
    if validation_errors:
        for err in validation_errors:
            st.warning(err)
    else:
        with st.spinner("Analyzing startup..."):
            try:
                analysis = service.analyze_startup(startup_name, website, description)
                scores = service.score_startup(description)
                investors = service.match_investors(description)
                memo = service.build_investment_memo(
                    startup_name=startup_name,
                    website=website,
                    analysis=analysis,
                    scores=scores,
                    investors=investors,
                )

                st.markdown("## Analysis")
                st.markdown(analysis)

                st.markdown("## Startup Scoring")
                metric_columns = st.columns(5)
                metric_columns[0].metric("Team", f"{scores['team_score']}/10")
                metric_columns[1].metric("Market", f"{scores['market_score']}/10")
                metric_columns[2].metric("Product", f"{scores['product_score']}/10")
                metric_columns[3].metric("Moat", f"{scores['moat_score']}/10")
                metric_columns[4].metric(
                    "Venture Potential", f"{scores['venture_potential_score']}/10"
                )

                st.markdown("## Suggested Investors")
                for investor in investors:
                    st.markdown(
                        f"- **{investor['name']}** — Focus: {', '.join(investor['focus'])}"
                        f" | Stage: {investor['stage']}"
                    )

                st.markdown("## Export Investment Memo")
                export_name = startup_name or "startup"
                st.download_button(
                    label="📄 Download Memo (TXT)",
                    data=memo,
                    file_name=f"{export_name}_investment_memo.txt",
                    mime="text/plain",
                )

                st.download_button(
                    label="📘 Download Memo (PDF)",
                    data=generate_simple_pdf(memo),
                    file_name=f"{export_name}_investment_memo.pdf",
                    mime="application/pdf",
                )

            except GeminiAuthError as exc:
                st.error("Authentication with Gemini failed.")
                st.info(
                    "Use a valid Google AI Studio API key starting with 'AIza' and "
                    "verify it is configured in Streamlit secrets."
                )
                st.caption(str(exc))
            except GeminiResponseError as exc:
                st.error("Gemini returned an invalid response.")
                st.caption(str(exc))
            except GeminiServiceError as exc:
                st.error("Gemini service encountered an error.")
                st.caption(str(exc))
            except Exception:
                st.error("Unexpected error while analyzing startup. Please try again.")

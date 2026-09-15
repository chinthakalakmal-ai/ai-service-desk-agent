import os
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Literal


# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------
st.set_page_config(
    page_title="AI Service Desk Agent",
    page_icon="🤖",
    layout="wide"
)


# -------------------------------------------------
# STRUCTURED GEMINI RESPONSE
# -------------------------------------------------
class TicketAnalysis(BaseModel):
    summary: str

    category: Literal[
        "Access / Password",
        "Network / VPN",
        "Hardware",
        "Software",
        "Email / Collaboration",
        "Security",
        "Business Application",
        "Other"
    ]

    priority: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    confidence: int

    priority_reason: str

    recommended_knowledge_article: str

    suggested_response: str


# -------------------------------------------------
# GET GEMINI API KEY
# -------------------------------------------------
def get_api_key():

    # First try environment variable
    api_key = os.getenv("GEMINI_API_KEY")

    # Fallback to Streamlit Secrets
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            api_key = None

    return api_key


# -------------------------------------------------
# GEMINI ANALYSIS FUNCTION
# -------------------------------------------------
def analyse_ticket(ticket_text):

    api_key = get_api_key()

    client = genai.Client(
        api_key=api_key
    )

    system_instruction = """
You are an AI Service Desk Assistant supporting an enterprise IT service desk.

Your role is to analyse incoming IT support tickets and provide recommendations
to a human service desk analyst.

For every ticket:

1. Create a short and accurate summary.
2. Assign the most appropriate category.
3. Recommend a priority.
4. Explain why the priority was selected.
5. Provide a confidence score from 0 to 100.
6. Recommend a relevant knowledge article title.
7. Draft a professional first-response message for the end user.

Priority guidance:

Critical:
A major business outage, serious cybersecurity incident, or critical service
unavailable to many users.

High:
Significant business impact, an important user cannot work, an urgent
customer-facing issue, or an important deadline is affected.

Medium:
A normal service disruption affecting productivity without immediate major
business impact.

Low:
A general request, information request, minor inconvenience, or non-urgent issue.

Important rules:

- Never claim an issue has already been fixed.
- Never claim an action has already been completed.
- Do not invent technical facts that are not present in the ticket.
- Treat your output as a recommendation only.
- The human service desk analyst remains responsible for the final decision.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",

        contents=ticket_text,

        config=types.GenerateContentConfig(
            system_instruction=system_instruction,

            response_mime_type="application/json",

            response_schema=TicketAnalysis,

        
        )
    )

    return TicketAnalysis.model_validate_json(
        response.text
    )


# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🤖 AI Service Desk Agent")

st.subheader(
    "Intelligent ITSM Ticket Analysis"
)

st.write(
    """
    This prototype demonstrates how generative AI can support service desk
    operations through ticket classification, prioritization, knowledge
    recommendations, and response suggestions while keeping humans responsible
    for final decisions.
    """
)

st.info(
    "🔐 AI recommendations require human review before any action is taken."
)

st.divider()


# -------------------------------------------------
# TICKET INPUT
# -------------------------------------------------
ticket = st.text_area(
    "Enter Service Desk Ticket",
    placeholder=(
        "Example: I cannot connect to the company VPN and I have "
        "an important customer meeting in 20 minutes."
    ),
    height=160
)


# -------------------------------------------------
# ANALYSE BUTTON
# -------------------------------------------------
if st.button(
    "🔍 Analyse Ticket",
    type="primary"
):

    if not ticket.strip():

        st.warning(
            "Please enter a service desk ticket."
        )

    elif not get_api_key():

        st.error(
            "Gemini API key was not found. "
            "Please configure GEMINI_API_KEY in Streamlit Secrets."
        )

    else:

        try:

            with st.spinner(
                "Gemini is analysing the ticket..."
            ):

                analysis = analyse_ticket(
                    ticket
                )

                st.session_state["analysis"] = analysis

                # Reset previous human decision
                if "decision" in st.session_state:
                    del st.session_state["decision"]

        except Exception as error:

            st.error(
                "The AI analysis could not be completed."
            )

            st.exception(error)


# -------------------------------------------------
# DISPLAY RESULTS
# -------------------------------------------------
if "analysis" in st.session_state:

    analysis = st.session_state["analysis"]

    st.success(
        "✅ AI analysis completed."
    )

    st.divider()

    left_column, right_column = st.columns(2)


    # -------------------------------------------------
    # LEFT COLUMN
    # -------------------------------------------------
    with left_column:

        st.subheader(
            "🧠 AI Analysis"
        )

        st.markdown(
            "### Summary"
        )

        st.write(
            analysis.summary
        )

        st.markdown(
            "### Category"
        )

        st.info(
            analysis.category
        )

        st.markdown(
            "### Suggested Priority"
        )

        if analysis.priority == "Critical":

            st.error(
                "🔴 Critical"
            )

        elif analysis.priority == "High":

            st.warning(
                "🟠 High"
            )

        elif analysis.priority == "Medium":

            st.info(
                "🟡 Medium"
            )

        else:

            st.success(
                "🟢 Low"
            )


        st.markdown(
            "### Confidence"
        )

        confidence_value = max(
            0,
            min(
                analysis.confidence,
                100
            )
        )

        st.progress(
            confidence_value / 100
        )

        st.write(
            f"**{confidence_value}% confidence**"
        )


        st.markdown(
            "### Priority Reason"
        )

        st.write(
            analysis.priority_reason
        )


    # -------------------------------------------------
    # RIGHT COLUMN
    # -------------------------------------------------
    with right_column:

        st.subheader(
            "📚 Recommended Action"
        )

        st.markdown(
            "### Suggested Knowledge Article"
        )

        st.info(
            analysis.recommended_knowledge_article
        )

        st.markdown(
            "### Suggested Response"
        )

        edited_response = st.text_area(
            "Review or edit the AI-generated response",
            value=analysis.suggested_response,
            height=280
        )


    # -------------------------------------------------
    # HUMAN REVIEW
    # -------------------------------------------------
    st.divider()

    st.subheader(
        "👤 Human Review"
    )

    st.write(
        """
        The AI recommendation must be reviewed by a human service desk
        analyst before any action is taken.
        """
    )

    approve_col, edit_col, reject_col = st.columns(3)


    with approve_col:

        if st.button(
            "✅ Approve Recommendation",
            use_container_width=True
        ):

            st.session_state["decision"] = "approved"


    with edit_col:

        if st.button(
            "✏️ Requires Editing",
            use_container_width=True
        ):

            st.session_state["decision"] = "edit"


    with reject_col:

        if st.button(
            "❌ Reject Recommendation",
            use_container_width=True
        ):

            st.session_state["decision"] = "rejected"


    # -------------------------------------------------
    # HUMAN DECISION RESULT
    # -------------------------------------------------
    if "decision" in st.session_state:

        decision = st.session_state["decision"]

        if decision == "approved":

            st.success(
                "✅ Human analyst approved the AI recommendation."
            )

            st.write(
                "**Approved Response:**"
            )

            st.write(
                edited_response
            )


        elif decision == "edit":

            st.warning(
                "✏️ Human analyst requested changes before action."
            )


        elif decision == "rejected":

            st.error(
                "❌ Human analyst rejected the AI recommendation."
            )


# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.divider()

st.caption(
    "AI Service Desk Agent | Human-in-the-loop ITSM automation"
)

st.caption(
    "Process first. AI second. Human accountability always."
)

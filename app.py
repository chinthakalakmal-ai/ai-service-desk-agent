import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Service Desk Agent",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# Structured AI response model
# -----------------------------
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


# -----------------------------
# AI analysis function
# -----------------------------
def analyse_ticket(ticket_text):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.responses.parse(
        model="gpt-5.6-luna",

        input=[
            {
                "role": "system",
                "content": """
You are an AI Service Desk Assistant supporting an enterprise IT service desk.

Analyse the user's IT support ticket.

Your job is to:

1. Create a concise summary.
2. Assign the most appropriate service desk category.
3. Recommend a priority.
4. Explain why that priority was selected.
5. Provide a confidence score between 0 and 100.
6. Recommend a relevant knowledge article title.
7. Draft a professional first-response message for the end user.

Priority guidance:

Critical:
Major business outage, severe cybersecurity incident, or critical service unavailable for many users.

High:
Significant business impact, important user unable to work, urgent customer-facing issue, or important deadline affected.

Medium:
Normal service disruption affecting productivity but with no major immediate business impact.

Low:
General request, minor inconvenience, information request, or non-urgent issue.

Never claim that an action has already been completed.

You are making recommendations only.

The final decision must remain with a human service desk analyst.
"""
            },

            {
                "role": "user",
                "content": ticket_text
            }
        ],

        text_format=TicketAnalysis
    )

    return response.output_parsed


# -----------------------------
# User interface
# -----------------------------
st.title("🤖 AI Service Desk Agent")

st.subheader("Intelligent ITSM Ticket Analysis")

st.write(
    """
    This prototype demonstrates how AI can support service desk operations
    through ticket classification, prioritization, knowledge recommendations,
    and response suggestions while keeping humans responsible for final decisions.
    """
)

st.info(
    "AI recommendations require human review before any action is taken."
)

st.divider()


# -----------------------------
# Ticket input
# -----------------------------
ticket = st.text_area(
    "Enter Service Desk Ticket",
    placeholder=(
        "Example: I cannot connect to the company VPN and I have "
        "an important customer meeting in 20 minutes."
    ),
    height=150
)


# -----------------------------
# Analyse button
# -----------------------------
if st.button("🔍 Analyse Ticket", type="primary"):

    if not ticket.strip():

        st.warning("Please enter a ticket description.")

    elif not os.getenv("OPENAI_API_KEY"):

        st.error(
            "OPENAI_API_KEY was not found. "
            "Please configure your API key securely."
        )

    else:

        try:

            with st.spinner("AI is analysing the ticket..."):

                analysis = analyse_ticket(ticket)

                st.session_state["analysis"] = analysis


        except Exception as e:

            st.error("The AI analysis could not be completed.")

            st.exception(e)


# -----------------------------
# Display analysis
# -----------------------------
if "analysis" in st.session_state:

    analysis = st.session_state["analysis"]

    st.success("AI analysis completed.")

    st.divider()

    col1, col2 = st.columns(2)

    # LEFT COLUMN
    with col1:

        st.subheader("🧠 AI Analysis")

        st.write("### Summary")
        st.write(analysis.summary)

        st.write("### Category")
        st.info(analysis.category)

        st.write("### Suggested Priority")

        if analysis.priority == "Critical":
            st.error("🔴 Critical")

        elif analysis.priority == "High":
            st.warning("🟠 High")

        elif analysis.priority == "Medium":
            st.info("🟡 Medium")

        else:
            st.success("🟢 Low")

        st.write("### Confidence")

        st.progress(
            min(
                max(
                    analysis.confidence,
                    0
                ),
                100
            ) / 100
        )

        st.write(
            f"**{analysis.confidence}% confidence**"
        )

        st.write("### Priority Reason")

        st.write(
            analysis.priority_reason
        )


    # RIGHT COLUMN
    with col2:

        st.subheader("📚 Recommended Action")

        st.write("### Suggested Knowledge Article")

        st.info(
            analysis.recommended_knowledge_article
        )

        st.write("### Suggested Response")

        st.text_area(
            "AI-generated draft",
            value=analysis.suggested_response,
            height=260
        )


    # -----------------------------
    # Human review
    # -----------------------------
    st.divider()

    st.subheader("👤 Human Review")

    st.write(
        "The AI recommendation must be reviewed before any action is taken."
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


    # -----------------------------
    # Decision result
    # -----------------------------
    if "decision" in st.session_state:

        decision = st.session_state["decision"]

        if decision == "approved":

            st.success(
                "Human analyst approved the AI recommendation."
            )

        elif decision == "edit":

            st.warning(
                "Human analyst requested changes before action."
            )

        elif decision == "rejected":

            st.error(
                "Human analyst rejected the AI recommendation."
            )


# -----------------------------
# Footer
# -----------------------------
st.divider()

st.caption(
    "Process first. AI second. Human accountability always."
)

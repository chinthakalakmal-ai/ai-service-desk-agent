import streamlit as st

st.set_page_config(
    page_title="AI Service Desk Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Service Desk Agent")

st.subheader("Intelligent ITSM Ticket Analysis")

st.write(
    """
    This prototype demonstrates how AI can support service desk operations
    through ticket classification, prioritization, knowledge recommendations,
    and response suggestions while keeping humans responsible for final decisions.
    """
)

st.divider()

ticket = st.text_area(
    "Enter Service Desk Ticket",
    placeholder="Example: I cannot connect to the VPN and I have an important customer meeting in 20 minutes.",
    height=150
)

if st.button("Analyse Ticket"):

    if not ticket.strip():
        st.warning("Please enter a ticket description.")

    else:
        st.success("Ticket received.")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("AI Analysis")

            st.write("**Category:** Network / VPN")
            st.write("**Suggested Priority:** High")
            st.write("**Confidence:** 92%")

            st.write(
                "**Summary:** User is unable to access the corporate VPN "
                "before a time-sensitive customer meeting."
            )

        with col2:
            st.subheader("Recommended Action")

            st.write("**Knowledge Article:** VPN Connectivity Troubleshooting")

            st.write(
                """
                **Suggested Response**

                Hi, I understand you're currently unable to connect to the
                corporate VPN and have an upcoming customer meeting.

                Please first confirm that you have an active internet
                connection and restart the VPN client.

                If the issue continues, the service desk can escalate the
                incident for immediate investigation.
                """
            )

        st.divider()

        st.subheader("Human Decision")

        approve, edit, reject = st.columns(3)

        with approve:
            st.button("✅ Approve")

        with edit:
            st.button("✏️ Edit")

        with reject:
            st.button("❌ Reject")

st.divider()

st.caption(
    "Process first. AI second. Human accountability always."
)

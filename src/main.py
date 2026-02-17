import streamlit as st
from auth.session_manager import SessionManager
from components.auth_pages import show_login_page
from components.sidebar import show_sidebar
from components.analysis_form import show_analysis_form
from components.footer import show_footer
from config.app_config import APP_NAME, APP_TAGLINE, APP_DESCRIPTION, APP_ICON, APP_LOGO
from services.ai_service import get_chat_response

# Must be the first Streamlit command
st.set_page_config(
    page_title=APP_NAME, page_icon=APP_LOGO, layout="wide"
)

# Initialize session state
SessionManager.init_session()

# Hide all Streamlit form-related elements
st.markdown(
    """
    <style>
        /* Hide form submission helper text */
        div[data-testid="InputInstructions"] > span:nth-child(1) {
            visibility: hidden;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Configure logo for sidebar (requires streamlit >= 1.35.0)
st.logo(APP_LOGO, icon_image=APP_LOGO)


def show_welcome_screen():
    st.markdown(
        """
        <style>
          .welcome-copy {
            text-align: center;
            max-width: 520px;
            margin: 0 auto;
          }
          .welcome-copy h1 { margin: 0.9rem 0 0.35rem 0; }
          .welcome-desc { font-size: 1.05rem; font-weight: 500; color: #E6E6E6; margin: 0.2rem 0; }
          .welcome-tagline { font-size: 0.98rem; color: #A8A8A8; margin: 0.25rem 0 1.1rem 0; }
          .welcome-hint { font-size: 0.92rem; color: #8A8A8A; margin: 0 0 1.25rem 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Visual centering on most screens (works well with the top greeting present)
    st.markdown("<div style='height: 8vh;'></div>", unsafe_allow_html=True)

    # One centered column for logo + text + button (keeps everything aligned)
    _, hero_col, _ = st.columns([1, 1.25, 1])
    with hero_col:
        st.image(APP_LOGO, width=220)

        st.markdown(
            f"""
            <div class="welcome-copy">
              <h1>{APP_NAME}</h1>
              <div class="welcome-desc">{APP_DESCRIPTION}</div>
              <div class="welcome-tagline">{APP_TAGLINE}</div>
              <div class="welcome-hint">Start by creating a new analysis session</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "➕ Create New Analysis Session",
            use_container_width=True,
            type="primary",
        ):
            success, session = SessionManager.create_chat_session()
            if success:
                st.session_state.current_session = session
                st.rerun()
            else:
                st.error("Failed to create session")


def show_chat_history():
    success, messages = st.session_state.auth_service.get_session_messages(
        st.session_state.current_session["id"]
    )

    if success:
        for msg in messages:
            # Skip system messages (they contain report text metadata)
            if msg.get("role") == "system":
                continue
            if msg["role"] == "user":
                st.info(msg["content"])
            else:
                st.success(msg["content"])
        return messages
    return []


def handle_chat_input(messages):
    if prompt := st.chat_input("Ask a follow-up question about the report..."):
        # Display user message immediately
        st.info(prompt)

        # Save user message
        st.session_state.auth_service.save_chat_message(
            st.session_state.current_session["id"], prompt, role="user"
        )

        # Get context (report text)
        # We try to get it from session state first (for immediate use)
        context_text = st.session_state.get("current_report_text", "")

        # If not in session state, try to retrieve from stored system message
        if not context_text and messages:
            for msg in messages:
                if msg.get("role") == "system" and "__REPORT_TEXT__" in msg.get(
                    "content", ""
                ):
                    # Extract report text from system message
                    content = msg.get("content", "")
                    start_idx = content.find("__REPORT_TEXT__\n") + len(
                        "__REPORT_TEXT__\n"
                    )
                    end_idx = content.find("\n__END_REPORT_TEXT__")
                    if start_idx > len("__REPORT_TEXT__\n") - 1 and end_idx > start_idx:
                        context_text = content[start_idx:end_idx]
                        # Also restore to session state for future use
                        st.session_state.current_report_text = context_text
                        break

        with st.spinner("Thinking..."):
            response = get_chat_response(prompt, context_text, messages)

            st.success(response)

            # Save AI response
            st.session_state.auth_service.save_chat_message(
                st.session_state.current_session["id"], response, role="assistant"
            )
            # Rerun to update history display properly
            st.rerun()


def show_user_greeting():
    if st.session_state.user:
        # Get name from user data, fallback to email if name is empty
        display_name = st.session_state.user.get("name") or st.session_state.user.get(
            "email", ""
        )
        st.markdown(
            f"""
            <div style='text-align: right; padding: 1rem; color: #64B5F6; font-size: 1.1em;'>
                👋 Hi, {display_name}
            </div>
        """,
            unsafe_allow_html=True,
        )


def main():
    SessionManager.init_session()

    if not SessionManager.is_authenticated():
        show_login_page()
        show_footer()
        return

    # Show user greeting at the top
    show_user_greeting()

    # Show sidebar
    show_sidebar()

    # Main chat area
    if st.session_state.get("current_session"):
        st.title(f"📊 {st.session_state.current_session['title']}")
        messages = show_chat_history()

        # If we have messages (meaning analysis is done), show chat input
        # Otherwise show analysis form
        if messages:
            # We can still show the analysis form collapsed or just hide it
            # For better UX, if analysis is done, we might not want to show the form again
            # unless the user wants to re-analyze/start over.
            # But the current form design allows re-analysis.
            # Let's put the analysis form in an expander if analysis is done.
            with st.expander("New Analysis / Update Report", expanded=False):
                show_analysis_form()

            handle_chat_input(messages)
        else:
            show_analysis_form()
    else:
        show_welcome_screen()


if __name__ == "__main__":
    main()

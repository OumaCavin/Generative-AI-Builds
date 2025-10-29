import streamlit as st;
import requests;

walker bootstrap_frontend(token: str) {
    # Page setup
    st.set_page_config(
        page_title="Task Manager Lite - AI Assistant",
        page_icon="📋",
        layout="wide"
    )

    st.title("📋 Task Manager Lite - AI Assistant")
    st.markdown("✨ Intelligent task management, email writing, and general chat — powered by an advanced AI assistant")

    # Session state
    if "task_results" not in st.session_state:
        st.session_state.task_results = []
    if "loading" not in st.session_state:
        st.session_state.loading = False

    # Prompt input section
    st.markdown("### 💭 What can I help you with today?")

    # Example requests
    with st.expander("💫 Example Requests"):
        st.markdown("**📋 Task Management**")
        if st.button("➕ Add a task"):
            st.session_state.user_input = "Add a task to buy groceries tomorrow at 3 PM"
        if st.button("📝 Summarize tasks"):
            st.session_state.user_input = "Summarize all my tasks"

        st.markdown("**📧 Email Writing**")
        if st.button("✉️ Write a meeting email"):
            st.session_state.user_input = "Write an email to schedule a meeting with my team for next Friday"
        if st.button("📬 Write follow-up email"):
            st.session_state.user_input = "Write a follow-up email for the project update"

        st.markdown("**💬 General Chat**")
        if st.button("🤔 Ask a question"):
            st.session_state.user_input = "What are the best practices for time management?"
        if st.button("🌟 Get advice"):
            st.session_state.user_input = "How can I be more productive at work?"

    # User input
    user_input = st.text_area(
        "💬 Enter your request:",
        value=st.session_state.get("user_input", ""),
        height=100,
        placeholder="e.g., Add a task to review the presentation by 5 PM tomorrow 📊"
    )

    # Process button
    if st.button("🚀 Process Request"):
        if user_input.strip():
            st.session_state.loading = True
            st.rerun()
        else:
            st.warning("⚠️ Please enter a request!")

    # Handle API request when loading
    if st.session_state.loading:
        with st.spinner("🧠 Processing your request..."):
            try:
                response = requests.post(
                    "http://localhost:8000/walker/task_manager",
                    json={"utterance": user_input},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    task_result = result.get("reports", [{}])[0]

                    # Update session results
		    st.session_state.task_results.insert(0, task_result)
                    st.session_state.task_results = st.session_state.task_results[:10]
                    st.session_state.loading = False

                    st.success("✅ Request processed successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Processing failed: {response.text}")
                    st.session_state.loading = False
            except requests.exceptions.Timeout:
                st.error("⏰ Request timed out. Please try again.")
                st.session_state.loading = False
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.loading = False

    # Display history
    if st.session_state.task_results:
        st.markdown("---")
        st.markdown("## 📊 Recent Activity")

        for i, result in enumerate(st.session_state.task_results):
            node_type = result.get("node_type", "Unknown")
            routed_to = result.get("routed_to", "")

            if node_type == "TaskHandling":
                icon, color = "📋", "blue"
            elif node_type == "EmailHandling":
                icon, color = "📧", "green"
            elif node_type == "GeneralChat":
                icon, color = "💬", "orange"
            else:
                icon, color = "🤖", "gray"

            with st.expander(f"{icon} {node_type} – Request {i+1}"):
                st.markdown(f"**🔀 Routed to:** `{routed_to}`")
                st.markdown("**👤 Your Request:**")
                st.info(result.get("utterance", "No input recorded"))

                st.markdown("**🤖 AI Response:**")
                response_text = result.get("response", "No response recorded")
                if response_text:
                    st.success(response_text)
                else:
                    st.warning("No response available")

                if st.button(f"📋 Copy Response {i+1}"):
                    st.write("📋 Response copied to clipboard! (Use Ctrl + C manually)")

        # Clear history
        if st.button("🗑️ Clear History"):
            st.session_state.task_results = []
            st.session_state.user_input = ""
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("**🤖 Powered by Task Manager Lite AI Assistant**")
    st.markdown("✨ Features: 📋 Task management • 📧 Email writing • 💬 Smart chat • 🔀 Intelligent routing")
}


entry {
    INSTANCE_URL = "http://localhost:8000";
    TEST_USER_EMAIL = "test@mail.com";
    TEST_USER_PASSWORD = "password";

    response = requests.post(
        f"{INSTANCE_URL}/user/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    );

    if response.status_code != 200 {
        response = requests.post(
            f"{INSTANCE_URL}/user/register",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        );
        assert response.status_code == 201;

# Try login or register   
     response = requests.post(
            f"{INSTANCE_URL}/user/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        );
        assert response.status_code == 200;
    }

    token = response.json()["token"];
    bootstrap_frontend(token);
}
